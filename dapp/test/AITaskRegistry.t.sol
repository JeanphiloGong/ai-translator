// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {AITaskRegistry} from "../src/AITaskRegistry.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockUSDT is ERC20 {
    constructor() ERC20("Tether USD", "USDT") {}

    function decimals() public pure override returns (uint8) {
        return 6;
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract AITaskRegistryTest is Test {
    MockUSDT private usdt;
    AITaskRegistry private registry;
    address private operator = address(0xBEEF);
    address private user = address(0xCAFE);

    function setUp() public {
        usdt = new MockUSDT();
        registry = new AITaskRegistry(address(usdt), operator);

        usdt.mint(user, 1_000_000);
        vm.prank(user);
        usdt.approve(address(registry), type(uint256).max);
    }

    function testCreateTaskTransfersFee() public {
        vm.prank(user);
        registry.createTask(bytes32("in"), bytes32("model"), 100);

        assertEq(usdt.balanceOf(address(registry)), 100);
    }

    function testSubmitResultOnlyOperator() public {
        vm.prank(user);
        uint256 taskId = registry.createTask(bytes32("in"), bytes32("model"), 100);

        vm.prank(operator);
        registry.submitResult(taskId, bytes32("out"));

        (, , bytes32 resultHash, , , AITaskRegistry.Status status, , ) = registry.tasks(taskId);
        assertEq(uint256(status), uint256(AITaskRegistry.Status.Completed));
        assertEq(resultHash, bytes32("out"));
    }

    function testSubmitResultRevertsForNonOperator() public {
        vm.prank(user);
        uint256 taskId = registry.createTask(bytes32("in"), bytes32("model"), 100);

        vm.expectRevert(AITaskRegistry.NotOperator.selector);
        registry.submitResult(taskId, bytes32("out"));
    }

    function testSubmitResultRevertsForInvalidTask() public {
        vm.prank(operator);
        vm.expectRevert(AITaskRegistry.BadStatus.selector);
        registry.submitResult(999, bytes32("out"));
    }
}
