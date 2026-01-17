package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	RPCURL             string
	ChainID            int64
	ContractAddress    string
	OperatorPrivateKey string
	Confirmations      uint64
	ReorgBuffer        uint64
	PollInterval       time.Duration
	PyAppURL           string
	PyAppAPIKey        string
	RequestTimeout     time.Duration
	RPCTimeout         time.Duration
	TxWaitTimeout      time.Duration
	DBPath             string
}

func Load() (Config, error) {
	cfg := Config{
		RPCURL:             os.Getenv("RPC_URL"),
		ContractAddress:    os.Getenv("AITASK_ADDRESS"),
		OperatorPrivateKey: os.Getenv("OPERATOR_PRIVATE_KEY"),
		PyAppURL:           os.Getenv("PYAPP_URL"),
		PyAppAPIKey:        os.Getenv("PYAPP_API_KEY"),
		DBPath:             getEnv("DB_PATH", "./data/orchestrator.db"),
		Confirmations:      getUint("CONFIRMATIONS", 2),
		ReorgBuffer:        getUint("REORG_BUFFER", 4),
		PollInterval:       getDuration("POLL_INTERVAL", 5*time.Second),
		RequestTimeout:     getDuration("REQUEST_TIMEOUT", 10*time.Second),
		RPCTimeout:         getDuration("RPC_TIMEOUT", 10*time.Second),
		TxWaitTimeout:      getDuration("TX_WAIT_TIMEOUT", 2*time.Minute),
	}

	if cfg.RPCURL == "" || cfg.ContractAddress == "" || cfg.OperatorPrivateKey == "" {
		return cfg, fmt.Errorf("RPC_URL, AITASK_ADDRESS, OPERATOR_PRIVATE_KEY are required")
	}
	if cfg.PyAppURL == "" {
		return cfg, fmt.Errorf("PYAPP_URL is required")
	}

	chainIDStr := os.Getenv("CHAIN_ID")
	if chainIDStr == "" {
		return cfg, fmt.Errorf("CHAIN_ID is required")
	}
	chainID, err := strconv.ParseInt(chainIDStr, 10, 64)
	if err != nil {
		return cfg, fmt.Errorf("invalid CHAIN_ID: %w", err)
	}
	cfg.ChainID = chainID

	return cfg, nil
}

func getEnv(key, def string) string {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	return v
}

func getUint(key string, def uint64) uint64 {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.ParseUint(v, 10, 64)
	if err != nil {
		return def
	}
	return n
}

func getDuration(key string, def time.Duration) time.Duration {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	d, err := time.ParseDuration(v)
	if err != nil {
		return def
	}
	return d
}
