const HDWalletProvider = require('truffle-hdwallet-provider');
const Web3 = require('web3');
const compiledProto = require('../ethereum/build/Prototype.json');

const provider = new HDWalletProvider(
  'wrong stand stadium easy follow exit spike music oval conduct produce knife',
  'https://rinkeby.infura.io/v3/a2269a6d6be241518fcddb60ca43cccd'
);
const web3 = new Web3(provider);


const tester = async () => {
  const accounts = await web3.eth.getAccounts();
  const instance = new web3.eth.Contract(
    JSON.parse(compiledProto.interface),
    "0x268F3dE17C9aFB5947d8AECc3a3Bb32c18a4676C"
  );

  instance.getPastEvents(
    'NewContent', {
    fromBlock: 0,
    toBlock: 'latest'
  }, function (error, events){ 
    if (error) {
      console.log(error); 
    }
  })
  .then(function(events){
    firstEventId = events[2]['returnValues']['contentId'];
    firstEventName = events[2]['returnValues']['name'];
    console.log(firstEventId, firstEventName);
    return [firstEventId, firstEventName];
  });
};

tester();
