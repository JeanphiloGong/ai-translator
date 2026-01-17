package tx

import (
	"context"
	"crypto/ecdsa"
	"fmt"
	"math/big"
	"strings"
	"sync"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
)

type Manager struct {
	client     *ethclient.Client
	chainID    *big.Int
	privateKey *ecdsa.PrivateKey
	mu         sync.Mutex
	nextNonce  *uint64
}

func NewManager(client *ethclient.Client, chainID int64, hexKey string) (*Manager, error) {
	key := strings.TrimPrefix(hexKey, "0x")
	pk, err := crypto.HexToECDSA(key)
	if err != nil {
		return nil, fmt.Errorf("invalid private key: %w", err)
	}
	return &Manager{
		client:     client,
		chainID:    big.NewInt(chainID),
		privateKey: pk,
	}, nil
}

func (m *Manager) TransactOpts(ctx context.Context) (*bind.TransactOpts, error) {
	nonce, err := m.nextNonce(ctx)
	if err != nil {
		return nil, err
	}

	auth, err := bind.NewKeyedTransactorWithChainID(m.privateKey, m.chainID)
	if err != nil {
		return nil, err
	}
	auth.Context = ctx
	auth.Nonce = new(big.Int).SetUint64(nonce)

	tip, err := m.client.SuggestGasTipCap(ctx)
	if err == nil {
		head, herr := m.client.HeaderByNumber(ctx, nil)
		if herr == nil && head.BaseFee != nil {
			feeCap := new(big.Int).Add(new(big.Int).Mul(tip, big.NewInt(2)), head.BaseFee)
			auth.GasTipCap = tip
			auth.GasFeeCap = feeCap
		}
	}
	return auth, nil
}

func (m *Manager) nextNonce(ctx context.Context) (uint64, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.nextNonce == nil {
		n, err := m.client.PendingNonceAt(ctx, m.FromAddress())
		if err != nil {
			return 0, err
		}
		m.nextNonce = &n
	}
	n := *m.nextNonce
	*m.nextNonce = n + 1
	return n, nil
}

func (m *Manager) ResetNonce() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.nextNonce = nil
}

func (m *Manager) FromAddress() common.Address {
	return crypto.PubkeyToAddress(m.privateKey.PublicKey)
}

func (m *Manager) Client() *ethclient.Client {
	return m.client
}
