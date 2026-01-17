package main

import (
	"context"
	"log"
	"os/signal"
	"syscall"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"

	"orchestrator/internal/chain"
	"orchestrator/internal/config"
	"orchestrator/internal/pyapp"
	"orchestrator/internal/runner"
	"orchestrator/internal/store"
	"orchestrator/internal/tx"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	client, err := ethclient.Dial(cfg.RPCURL)
	if err != nil {
		log.Fatal(err)
	}

	contract, err := chain.NewContract(client, common.HexToAddress(cfg.ContractAddress))
	if err != nil {
		log.Fatal(err)
	}

	st, err := store.NewSQLite(cfg.DBPath)
	if err != nil {
		log.Fatal(err)
	}
	if err := st.Init(context.Background()); err != nil {
		log.Fatal(err)
	}

	txmgr, err := tx.NewManager(client, cfg.ChainID, cfg.OperatorPrivateKey)
	if err != nil {
		log.Fatal(err)
	}

	py := pyapp.NewClient(cfg.PyAppURL, cfg.PyAppAPIKey, cfg.RequestTimeout)
	run := runner.New(contract, txmgr, py, uint64(cfg.ChainID), cfg.RPCTimeout, cfg.TxWaitTimeout)
	poller := chain.NewPoller(client, contract, st, uint64(cfg.ChainID), cfg.Confirmations, cfg.ReorgBuffer, cfg.PollInterval, cfg.RPCTimeout)

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := poller.Run(ctx, run); err != nil && err != context.Canceled {
		log.Fatal(err)
	}
}
