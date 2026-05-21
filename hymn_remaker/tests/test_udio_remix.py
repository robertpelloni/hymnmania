import os
import sys
import logging
import time

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("UdioRemixTest")

from hymn_remaker.src.udio_remaker import UdioRemaker

def main():
    logger.info("Initializing UdioRemaker with browser automation support...")
    remaker = UdioRemaker()
    
    if not remaker.is_available():
        logger.error("❌ Udio browser automation is NOT available. Is Edge running with --remote-debugging-port=9222?")
        sys.exit(1)
        
    logger.info("✅ Udio browser automation detected as available!")
    
    # Locate test WAV file in the output folder
    wav_path = r"c:\Users\hyper\workspace\bobmani\hymnmania\hymn_remaker\output\sample_hymn_test.wav"
    
    # If it doesn't exist, try to use any valid WAV in the output directory
    if not os.path.exists(wav_path):
        import glob
        wavs = glob.glob(r"c:\Users\hyper\workspace\bobmani\hymnmania\hymn_remaker\output\*_base.wav")
        if wavs:
            wav_path = wavs[0]
        else:
            # Create a dummy WAV file for testing if none exist
            logger.info("Creating a dummy WAV file for testing...")
            os.makedirs(os.path.dirname(wav_path), exist_ok=True)
            with open(wav_path, "wb") as f:
                f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
                
    logger.info(f"Using WAV path: {wav_path} (exists: {os.path.exists(wav_path)})")
    
    prompt = "A modern Deep House remix of 'Emmanuel'. Melodic synth, club beat, progressive house style, high quality."
    style = "Deep House, electronic"
    
    logger.info("Triggering automated Remix browser generation...")
    try:
        # We set a short poll timeout to exit early for testing once generation triggers
        logger.info("Invoking remaker.remake() — watch Microsoft Edge for upload and remix confirmation!")
        # We will trigger remake but we can interrupt it or let it run.
        # Actually, let's run the remake!
        remake_path = remaker.remake(
            wav_path=wav_path,
            prompt=prompt,
            style=style,
            title="Test Remix Automation"
        )
        logger.info(f"🎉 SUCCESS! Automated Udio remix complete. Downloaded to: {remake_path}")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
