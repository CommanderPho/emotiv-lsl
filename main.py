from emotiv_lsl.emotiv_epoc_x import EmotivEpocX

if __name__ == "__main__":
    emotiv_epoc_x = EmotivEpocX()
    crypto_key = emotiv_epoc_x.get_crypto_key()
    print(f'crypto_key: {crypto_key}')
    emotiv_epoc_x.main_loop()
