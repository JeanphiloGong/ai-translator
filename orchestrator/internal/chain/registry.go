package chain

import (
	"context"
	_ "embed"
	"fmt"
	"math/big"
	"strings"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
)

//go:embed ../../contracts/AITaskRegistry.json
var abiJSON string

type Contract struct {
	address            common.Address
	client             *ethclient.Client
	abi                abi.ABI
	bound              *bind.BoundContract
	taskCreatedEvent   abi.Event
	taskCompletedEvent abi.Event
}

type TaskCreatedEvent struct {
	TaskId    *big.Int
	Requester common.Address
	InputHash [32]byte
	Model     [32]byte
	Fee       *big.Int
	Raw       types.Log
}

type TaskCompletedEvent struct {
	TaskId     *big.Int
	ResultHash [32]byte
	Raw        types.Log
}

func NewContract(client *ethclient.Client, address common.Address) (*Contract, error) {
	parsed, err := abi.JSON(strings.NewReader(abiJSON))
	if err != nil {
		return nil, fmt.Errorf("parse ABI: %w", err)
	}

	bound := bind.NewBoundContract(address, parsed, client, client, client)
	taskCreated, ok := parsed.Events["TaskCreated"]
	if !ok {
		return nil, fmt.Errorf("ABI missing TaskCreated event")
	}
	taskCompleted, ok := parsed.Events["TaskCompleted"]
	if !ok {
		return nil, fmt.Errorf("ABI missing TaskCompleted event")
	}

	return &Contract{
		address:            address,
		client:             client,
		abi:                parsed,
		bound:              bound,
		taskCreatedEvent:   taskCreated,
		taskCompletedEvent: taskCompleted,
	}, nil
}

func (c *Contract) FilterTaskCreated(ctx context.Context, start, end uint64) ([]*TaskCreatedEvent, error) {
	query := ethereum.FilterQuery{
		FromBlock: new(big.Int).SetUint64(start),
		ToBlock:   new(big.Int).SetUint64(end),
		Addresses: []common.Address{c.address},
		Topics:    [][]common.Hash{{c.taskCreatedEvent.ID}},
	}
	logs, err := c.client.FilterLogs(ctx, query)
	if err != nil {
		return nil, err
	}

	events := make([]*TaskCreatedEvent, 0, len(logs))
	for _, lg := range logs {
		ev, err := c.ParseTaskCreated(lg)
		if err != nil {
			return nil, err
		}
		events = append(events, ev)
	}
	return events, nil
}

func (c *Contract) ParseTaskCreated(lg types.Log) (*TaskCreatedEvent, error) {
	if len(lg.Topics) == 0 || lg.Topics[0] != c.taskCreatedEvent.ID {
		return nil, fmt.Errorf("log is not TaskCreated")
	}
	out := TaskCreatedEvent{Raw: lg}
	if err := c.abi.UnpackIntoInterface(&out, "TaskCreated", lg.Data); err != nil {
		return nil, err
	}

	indexed := make(abi.Arguments, 0)
	for _, arg := range c.taskCreatedEvent.Inputs {
		if arg.Indexed {
			indexed = append(indexed, arg)
		}
	}
	if len(indexed) > 0 {
		if err := abi.ParseTopics(&out, indexed, lg.Topics[1:]); err != nil {
			return nil, err
		}
	}
	return &out, nil
}

func (c *Contract) SubmitResult(auth *bind.TransactOpts, taskID *big.Int, resultHash [32]byte) (*types.Transaction, error) {
	return c.bound.Transact(auth, "submitResult", taskID, resultHash)
}
