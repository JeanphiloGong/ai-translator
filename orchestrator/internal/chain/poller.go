package chain

import (
	"context"
	"time"

	"github.com/ethereum/go-ethereum/ethclient"

	"orchestrator/internal/store"
)

type TaskHandler interface {
	HandleTask(ctx context.Context, ev *TaskCreatedEvent) error
}

type Poller struct {
	client        *ethclient.Client
	contract      *Contract
	store         store.Store
	chainID       uint64
	confirmations uint64
	reorgBuffer   uint64
	pollInterval  time.Duration
	rpcTimeout    time.Duration
}

func NewPoller(client *ethclient.Client, contract *Contract, store store.Store, chainID uint64, confirmations, reorgBuffer uint64, pollInterval, rpcTimeout time.Duration) *Poller {
	return &Poller{
		client:        client,
		contract:      contract,
		store:         store,
		chainID:       chainID,
		confirmations: confirmations,
		reorgBuffer:   reorgBuffer,
		pollInterval:  pollInterval,
		rpcTimeout:    rpcTimeout,
	}
}

func (p *Poller) Run(ctx context.Context, handler TaskHandler) error {
	ticker := time.NewTicker(p.pollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			if err := p.pollOnce(ctx, handler); err != nil {
				return err
			}
		}
	}
}

func (p *Poller) pollOnce(ctx context.Context, handler TaskHandler) error {
	rpcCtx, cancel := context.WithTimeout(ctx, p.rpcTimeout)
	head, err := p.client.HeaderByNumber(rpcCtx, nil)
	cancel()
	if err != nil {
		return err
	}
	if head.Number.Uint64() <= p.confirmations {
		return nil
	}
	safeEnd := head.Number.Uint64() - p.confirmations

	var start uint64
	last, ok, err := p.store.GetCheckpoint(ctx)
	if err != nil {
		return err
	}
	if ok && last > p.reorgBuffer {
		start = last - p.reorgBuffer
	}
	if start > safeEnd {
		return nil
	}

	rpcCtx, cancel = context.WithTimeout(ctx, p.rpcTimeout)
	events, err := p.contract.FilterTaskCreated(rpcCtx, start, safeEnd)
	cancel()
	if err != nil {
		return err
	}

	for _, ev := range events {
		seen, err := p.store.SeenLog(ctx, p.chainID, ev.Raw.TxHash, ev.Raw.Index)
		if err != nil {
			return err
		}
		if seen {
			continue
		}
		if err := handler.HandleTask(ctx, ev); err != nil {
			return err
		}
		if err := p.store.MarkLog(ctx, p.chainID, ev.Raw.TxHash, ev.Raw.Index, ev.Raw.BlockNumber); err != nil {
			return err
		}
	}

	return p.store.SaveCheckpoint(ctx, safeEnd)
}
