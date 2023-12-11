// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

contract FirmwareUpdate {

    mapping(string => string) public deviceToFirmwareMapping;

    function getLatestFirmwareHash(string memory device) public view returns (string memory) {
        return deviceToFirmwareMapping[device];
    }
    
    function storeFirmware(string memory ipfsHash, string memory device) public payable {
        // Store IPFS hash on the blockchain
        deviceToFirmwareMapping[device] = ipfsHash;
    }

}
