package runner

import (
	"context"
	"fmt"
	"time"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"

	"orchestrator/internal/chain"
	"orchestrator/internal/pyapp"
	"orchestrator/internal/tx"
)

type Runner struct {
	contract      *chain.Contract
	txmgr         *tx.Manager
	pyapp         *pyapp.Client
	chainID       uint64
	rpcTimeout    time.Duration
	txWaitTimeout time.Duration
}

func New(contract *chain.Contract, txmgr *tx.Manager, py *pyapp.Client, chainID uint64, rpcTimeout, txWaitTimeout time.Duration) *Runner {
	return &Runner{
		contract:      contract,
		txmgr:         txmgr,
		pyapp:         py,
		chainID:       chainID,
		rpcTimeout:    rpcTimeout,
		txWaitTimeout: txWaitTimeout,
	}
}

func (r *Runner) HandleTask(ctx context.Context, ev *chain.TaskCreatedEvent) error {
	taskID, err := pyapp.TaskIDToUint64(ev.TaskId)
	if err != nil {
		return err
	}

	inputHash := common.BytesToHash(ev.InputHash[:])
	model := common.BytesToHash(ev.Model[:]).Hex()
	requester := ev.Requester.Hex()

	claimReq := pyapp.ClaimTaskRequest{
		TaskID:      taskID,
		InputHash:   inputHash.Hex(),
		Requester:   requester,
		Model:       model,
		Fee:         ev.Fee.String(),
		ChainID:     r.chainID,
		TxHash:      ev.Raw.TxHash.Hex(),
		BlockNumber: ev.Raw.BlockNumber,
	}
	if _, err := r.pyapp.ClaimTask(ctx, claimReq); err != nil {
		return err
	}

	input, err := r.pyapp.GetInput(ctx, inputHash)
	if err != nil {
		return err
	}

	translation, err := r.pyapp.RunModel(ctx, input.InputPayload.Mode, input.InputPayload.Text, input.InputPayload.IncludeGrammar)
	if err != nil {
		return err
	}

	payload := pyapp.ResultPayload{
		OriginalText:          translation.OriginalText,
		TranslatedText:        translation.TranslatedText,
		EnglishGrammar:        translation.EnglishGrammar,
		JapaneseText:          translation.JapaneseText,
		HiraganaPronunciation: translation.HiraganaPronunciation,
		JapaneseGrammar:       translation.JapaneseGrammar,
		Timestamp:             translation.Timestamp.UTC().Format("2006-01-02T15:04:05Z"),
	}

	resultHash, err := r.pyapp.SubmitResult(ctx, taskID, payload)
	if err != nil {
		return err
	}
	if resultHash == (common.Hash{}) {
		return fmt.Errorf("empty result hash from pyapp")
	}

	rpcCtx, cancel := context.WithTimeout(ctx, r.rpcTimeout)
	auth, err := r.txmgr.TransactOpts(rpcCtx)
	if err != nil {
		cancel()
		return err
	}

	hash := [32]byte(resultHash)
	tx, err := r.contract.SubmitResult(auth, ev.TaskId, hash)
	cancel()
	if err != nil {
		return err
	}

	waitCtx, cancel := context.WithTimeout(ctx, r.txWaitTimeout)
	defer cancel()
	receipt, err := bind.WaitMined(waitCtx, r.txmgr.Client(), tx)
	if err != nil {
		return err
	}
	if receipt.Status != types.ReceiptStatusSuccessful {
		return fmt.Errorf("submitResult failed: tx=%s", tx.Hash().Hex())
	}
	return nil
}
