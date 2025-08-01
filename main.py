import logging
from emotiv_lsl.emotiv_epoc_x import EmotivEpocX

if __name__ == "__main__":
    # Configure logging for debugging data packets
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    emotiv_epoc_x = EmotivEpocX()
    crypto_key = emotiv_epoc_x.get_crypto_key()
    print(f'crypto_key: {crypto_key}')
    emotiv_epoc_x.main_loop()
