pragma solitity ^0.4.25;

interface IERC165 {
  function supportsInterface(bytes4 interfaceId) external view returns (bool);
}
