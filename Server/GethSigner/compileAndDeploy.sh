#!/bin/sh

solc --bin --abi --optimize --output-dir ./output ./smartContract.sol
python3 deployContract.py