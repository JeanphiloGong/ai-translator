package store

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/ethereum/go-ethereum/common"
	_ "modernc.org/sqlite"
)

type Store interface {
	Init(ctx context.Context) error
	GetCheckpoint(ctx context.Context) (uint64, bool, error)
	SaveCheckpoint(ctx context.Context, block uint64) error
	SeenLog(ctx context.Context, chainID uint64, txHash common.Hash, logIndex uint) (bool, error)
	MarkLog(ctx context.Context, chainID uint64, txHash common.Hash, logIndex uint, blockNumber uint64) error
}

type SQLiteStore struct {
	db *sql.DB
}

func NewSQLite(path string) (*SQLiteStore, error) {
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, err
	}
	return &SQLiteStore{db: db}, nil
}

func (s *SQLiteStore) Init(ctx context.Context) error {
	_, err := s.db.ExecContext(ctx, `
CREATE TABLE IF NOT EXISTS checkpoints (
  id INTEGER PRIMARY KEY,
  last_block INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS processed_logs (
  chain_id INTEGER NOT NULL,
  tx_hash TEXT NOT NULL,
  log_index INTEGER NOT NULL,
  block_number INTEGER NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(chain_id, tx_hash, log_index)
);`)
	return err
}

func (s *SQLiteStore) GetCheckpoint(ctx context.Context) (uint64, bool, error) {
	row := s.db.QueryRowContext(ctx, `SELECT last_block FROM checkpoints WHERE id = 1`)
	var v uint64
	err := row.Scan(&v)
	if err == sql.ErrNoRows {
		return 0, false, nil
	}
	if err != nil {
		return 0, false, err
	}
	return v, true, nil
}

func (s *SQLiteStore) SaveCheckpoint(ctx context.Context, block uint64) error {
	_, err := s.db.ExecContext(ctx, `
INSERT INTO checkpoints (id, last_block) VALUES (1, ?)
ON CONFLICT(id) DO UPDATE SET last_block = excluded.last_block;
`, block)
	return err
}

func (s *SQLiteStore) SeenLog(ctx context.Context, chainID uint64, txHash common.Hash, logIndex uint) (bool, error) {
	row := s.db.QueryRowContext(ctx, `
SELECT 1 FROM processed_logs WHERE chain_id = ? AND tx_hash = ? AND log_index = ? LIMIT 1;
`, chainID, txHash.Hex(), logIndex)
	var one int
	err := row.Scan(&one)
	if err == sql.ErrNoRows {
		return false, nil
	}
	return err == nil, err
}

func (s *SQLiteStore) MarkLog(ctx context.Context, chainID uint64, txHash common.Hash, logIndex uint, blockNumber uint64) error {
	_, err := s.db.ExecContext(ctx, `
INSERT OR IGNORE INTO processed_logs (chain_id, tx_hash, log_index, block_number)
VALUES (?, ?, ?, ?);
`, chainID, txHash.Hex(), logIndex, blockNumber)
	if err != nil {
		return fmt.Errorf("mark log failed: %w", err)
	}
	return nil
}
