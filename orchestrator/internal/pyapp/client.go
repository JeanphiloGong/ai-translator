package pyapp

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"math/big"
	"net/http"
	"strings"
	"time"

	"github.com/ethereum/go-ethereum/common"
)

type Client struct {
	baseURL string
	apiKey  string
	http    *http.Client
}

func NewClient(baseURL, apiKey string, timeout time.Duration) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		apiKey:  apiKey,
		http:    &http.Client{Timeout: timeout},
	}
}

type APIError struct {
	Status  int
	Code    string `json:"code"`
	Message string `json:"message"`
}

func (e *APIError) Error() string {
	if e.Code != "" {
		return fmt.Sprintf("pyapp error: status=%d code=%s message=%s", e.Status, e.Code, e.Message)
	}
	return fmt.Sprintf("pyapp error: status=%d message=%s", e.Status, e.Message)
}

func IsStatus(err error, status int) bool {
	apiErr, ok := err.(*APIError)
	return ok && apiErr.Status == status
}

type ClaimTaskRequest struct {
	TaskID      uint64 `json:"task_id"`
	InputHash   string `json:"input_hash"`
	Requester   string `json:"requester"`
	Model       string `json:"model"`
	Fee         string `json:"fee"`
	ChainID     uint64 `json:"chain_id"`
	TxHash      string `json:"tx_hash"`
	BlockNumber uint64 `json:"block_number"`
}

type ClaimTaskResponse struct {
	TaskID    uint64 `json:"task_id"`
	Status    string `json:"status"`
	UpdatedAt string `json:"updated_at"`
}

func (c *Client) ClaimTask(ctx context.Context, req ClaimTaskRequest) (*ClaimTaskResponse, error) {
	var out ClaimTaskResponse
	if err := c.doJSON(ctx, http.MethodPost, "/tasks/claim", req, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

type InputPayload struct {
	Text           string `json:"text"`
	Mode           string `json:"mode"`
	IncludeGrammar bool   `json:"include_grammar"`
}

type InputResponse struct {
	InputHash    string       `json:"input_hash"`
	InputPayload InputPayload `json:"input_payload"`
	PreparedAt   string       `json:"prepared_at"`
}

func (c *Client) GetInput(ctx context.Context, inputHash common.Hash) (*InputResponse, error) {
	var out InputResponse
	path := fmt.Sprintf("/tasks/input/%s", inputHash.Hex())
	if err := c.doJSON(ctx, http.MethodGet, path, nil, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

type TextRequest struct {
	Text           string `json:"text"`
	IncludeGrammar bool   `json:"include_grammar"`
}

type TranslationResponse struct {
	OriginalText          string    `json:"original_text"`
	TranslatedText        string    `json:"translated_text"`
	EnglishGrammar        *string   `json:"english_grammar"`
	JapaneseText          *string   `json:"japanese_text"`
	HiraganaPronunciation *string   `json:"hiragana_pronunciation"`
	JapaneseGrammar       *string   `json:"japanese_grammar"`
	Timestamp             time.Time `json:"timestamp"`
}

func (c *Client) RunModel(ctx context.Context, mode string, text string, includeGrammar bool) (*TranslationResponse, error) {
	path := ""
	switch mode {
	case "translate-zh":
		path = "/translate/chinese"
	case "correct-en":
		path = "/correct/english"
	default:
		return nil, fmt.Errorf("unsupported mode: %s", mode)
	}

	req := TextRequest{
		Text:           text,
		IncludeGrammar: includeGrammar,
	}
	var out TranslationResponse
	if err := c.doJSON(ctx, http.MethodPost, path, req, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

type ResultPayload struct {
	OriginalText          string  `json:"original_text"`
	TranslatedText        string  `json:"translated_text"`
	EnglishGrammar        *string `json:"english_grammar"`
	JapaneseText          *string `json:"japanese_text"`
	HiraganaPronunciation *string `json:"hiragana_pronunciation"`
	JapaneseGrammar       *string `json:"japanese_grammar"`
	Timestamp             string  `json:"timestamp"`
}

type SubmitResultRequest struct {
	ResultPayload ResultPayload `json:"result_payload"`
	ResultHash    string        `json:"result_hash,omitempty"`
}

type SubmitResultResponse struct {
	TaskID      uint64 `json:"task_id"`
	ResultHash  string `json:"result_hash"`
	Status      string `json:"status"`
	CompletedAt string `json:"completed_at"`
}

func (c *Client) SubmitResult(ctx context.Context, taskID uint64, payload ResultPayload) (common.Hash, error) {
	var out SubmitResultResponse
	path := fmt.Sprintf("/tasks/%d/result", taskID)
	req := SubmitResultRequest{ResultPayload: payload}
	if err := c.doJSON(ctx, http.MethodPost, path, req, &out); err != nil {
		return common.Hash{}, err
	}
	return common.HexToHash(out.ResultHash), nil
}

func (c *Client) doJSON(ctx context.Context, method, path string, in any, out any) error {
	var body *bytes.Reader
	if in != nil {
		b, err := json.Marshal(in)
		if err != nil {
			return err
		}
		body = bytes.NewReader(b)
	} else {
		body = bytes.NewReader(nil)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, body)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("X-API-KEY", c.apiKey)
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		apiErr := &APIError{Status: resp.StatusCode}
		_ = json.NewDecoder(resp.Body).Decode(apiErr)
		if apiErr.Message == "" {
			apiErr.Message = resp.Status
		}
		return apiErr
	}

	if out == nil {
		return nil
	}
	return json.NewDecoder(resp.Body).Decode(out)
}

func TaskIDToUint64(id *big.Int) (uint64, error) {
	if id == nil {
		return 0, fmt.Errorf("task id is nil")
	}
	if id.BitLen() > 64 {
		return 0, fmt.Errorf("task id too large: %s", id.String())
	}
	return id.Uint64(), nil
}
