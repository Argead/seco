import web3 from './web3';
import Prototype from './build/Prototype.json';

const instance = new web3.eth.Contract(
  JSON.parse(Prototype.interface),
  "0x268F3dE17C9aFB5947d8AECc3a3Bb32c18a4676C"
);

export default instance;
