// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {AITaskRegistry} from "../src/AITaskRegistry.sol";

contract DeployScript is Script {
    function run() public {
        address usdt = vm.envAddress("USDT_ADDRESS");
        address operator = vm.envAddress("OPERATOR_ADDRESS");

        vm.startBroadcast();
        new AITaskRegistry(usdt, operator);
        vm.stopBroadcast();
    }
}

