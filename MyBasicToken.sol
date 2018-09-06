pragma solidity ^0.4.18;

import 'BasicToken.sol';

contract MyBasicToken is BasicToken {
  uint public constant decimals = 18;

  uint256 public constant INITIAL_SUPPLY = 10000 * (10 ** uint256(decimals));

  function MyBasicToken() public {
    totalSupply_ = INITIAL_SUPPLY;
    balances[msg.sender] = INITIAL_SUPPLY;
    emit Transfer(0x0, msg.sender,INITIAL_SUPPLY);
  }
}
