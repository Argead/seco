pragma solidity ^0.4.25;

contract Prototype {
    event NewContent(address owner, uint256 contentId, string name);

    Content[] textContent;

    struct Content {
      string name;
    }
 
    address public owner;


    constructor () public {
      owner = msg.sender;
    }

    function createContent(string _name) public returns (uint) {
      Content memory _content = Content({
        name: _name
      });
      uint256 newContentId = textContent.push(_content) - 1;
      require(newContentId == uint256(uint32(newContentId)));
      emit NewContent(msg.sender, newContentId, _name);
      return newContentId;
    }
}
