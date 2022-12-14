// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0 <0.9.0;

contract BotnetContract {

    address public owner;

    //TODO: include ip, state variables
    struct Worker {
        string key;
    }

    //TODO: mapping (string => Worker) public stringToWorker;
    Worker[] public workers;


    event joinRequest(string workerKey);

    event commandAdded(string workerKey, string cmd);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner);  
        _;
    }

    function addWorker(string memory workerKey) onlyOwner public {
        //TODO: check does not already exits
        workers.push(Worker({key: workerKey}));
        //TODO: stringToWorker[workerKey] = Worker({key: workerKey});
    }

    function addCommand(string memory workerKey, string memory cmd) onlyOwner public {
        emit commandAdded(workerKey, cmd);
    }

    function join(string memory workerKey) public{
        emit joinRequest(workerKey);
    }
    
}