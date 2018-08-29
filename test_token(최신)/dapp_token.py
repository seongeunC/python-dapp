import time
from web3 import Web3, HTTPProvider
from solc import compile_files

rpc_url = "http://192.168.0.223:8545"
w3 = Web3(HTTPProvider(rpc_url))

w3.personal.unlockAccount(w3.eth.accounts[0], "account1", 0)
#w3.personal.unlockAccount(w3.eth.accounts[1], "pass1", 0)

## deploy_contract
class mytoken:
    def __init__(self,contract_file_name,contract_name):
        compiled_sol = compile_files([contract_file_name])
        contract_interface = compiled_sol['{}:{}'.format(contract_file_name,contract_name)]

        contract = w3.eth.contract(abi= contract_interface['abi'],
                                   bytecode= contract_interface['bin'],
                                   bytecode_runtime= contract_interface['bin-runtime'])
        tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0]})
        self.mining(2)
        tx_recepit = w3.eth.getTransactionReceipt(tx_hash)
        contract_address = tx_recepit['contractAddress']
        self.contract_instance = contract(contract_address)

    def send_token(self,sender,to,value):
        self.contract_instance.functions.transfer(to,value).transact({'from':sender})
        self.mining(2)


    def show_token(self,addr):
        return self.contract_instance.call().balanceOf(addr)

    def show_total_token(self):
        return self.contract_instance.call().totalSupply()

    def mining(self,thread):
        n_blockNumber = w3.eth.blockNumber
        while True:
            if w3.eth.blockNumber == n_blockNumber+1:
                w3.miner.stop()
                break
            else:
                w3.miner.start(thread)


# 토큰 생성
#seongeun_token = mytoken('MyBasicToken.sol','MyBasicToken')

# 젠체 발행된 토큰 계수 확인
#seongeun_token.show_total_token()

# 토큰 보내기 ( 0번 계정에서 1번계정으로 1000000000000000000000개 토큰 보내기)
#seongeun_token.send_token(w3.eth.accounts[0],w3.eth.accounts[1],1000000000000000000000)

# 계정 토큰 수 확인 ( 0번 계정의 토큰 수 확인)
#seongeun_token.show_token(Web3.toChecksumAddress(0x3ab733d78f63860fd5e5e672bc7648c764051df3))
