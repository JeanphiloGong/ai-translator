// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract AITaskRegistry is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    error ZeroAddress();
    error InvalidHash();
    error InvalidFee();
    error NotOperator();
    error BadStatus();

    enum Status {
        None,
        Created,
        Completed,
        Refunded
    }

    struct Task {
        address requester;
        bytes32 inputHash;
        bytes32 resultHash;
        bytes32 model;
        uint256 fee;
        Status status;
        uint64 createdAt;
        uint64 completedAt;
    }

    IERC20 public immutable usdt;
    address public operator;
    uint256 public taskCount;
    mapping(uint256 => Task) public tasks;

    event TaskCreated(
        uint256 indexed taskId,
        address indexed requester,
        bytes32 indexed inputHash,
        bytes32 model,
        uint256 fee
    );
    event TaskCompleted(uint256 indexed taskId, bytes32 resultHash);
    event OperatorUpdated(address indexed operator);

    constructor(address usdt_, address operator_) Ownable(msg.sender) {
        if (usdt_ == address(0) || operator_ == address(0)) revert ZeroAddress();
        usdt = IERC20(usdt_);
        operator = operator_;
    }

    modifier onlyOperator() {
        if (msg.sender != operator) revert NotOperator();
        _;
    }

    function setOperator(address operator_) external onlyOwner {
        if (operator_ == address(0)) revert ZeroAddress();
        operator = operator_;
        emit OperatorUpdated(operator_);
    }

    function createTask(bytes32 inputHash, bytes32 model, uint256 fee)
        external
        nonReentrant
        returns (uint256 taskId)
    {
        if (inputHash == bytes32(0)) revert InvalidHash();
        if (fee == 0) revert InvalidFee();

        taskId = ++taskCount;
        tasks[taskId] = Task({
            requester: msg.sender,
            inputHash: inputHash,
            resultHash: bytes32(0),
            model: model,
            fee: fee,
            status: Status.Created,
            createdAt: uint64(block.timestamp),
            completedAt: 0
        });

        usdt.safeTransferFrom(msg.sender, address(this), fee);
        emit TaskCreated(taskId, msg.sender, inputHash, model, fee);
    }

    function submitResult(uint256 taskId, bytes32 resultHash)
        external
        nonReentrant
        onlyOperator
    {
        if (resultHash == bytes32(0)) revert InvalidHash();

        Task storage t = tasks[taskId];
        if (t.status != Status.Created) revert BadStatus();

        t.resultHash = resultHash;
        t.status = Status.Completed;
        t.completedAt = uint64(block.timestamp);

        emit TaskCompleted(taskId, resultHash);
    }
}
