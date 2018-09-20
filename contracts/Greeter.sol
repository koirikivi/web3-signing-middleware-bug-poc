pragma solidity ^0.4.0;

contract Greeter {
    string public greeting;

    // TODO: Populus seems to get no bytecode if `internal`
    function Greeter() public {
        greeting = 'Hello';
    }

    function setGreeting(string _greeting) public {
        greeting = _greeting;
    }

    function greet() public returns (string) {
        return greeting;
    }

    function payForNothing() public payable returns (uint256) {
        return msg.value;
    }
}
