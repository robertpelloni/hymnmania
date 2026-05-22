import websocket
import json

def click_udio_confirm():
    # Using the current Udio tab ID found in previous steps
    ws_url = "ws://localhost:9222/devtools/page/99D8C336B5F863B4E3401FFACB11C4D5"
    
    script = """
    (function() {
        console.log('Gemini: Attempting to clear Udio popup...');
        
        // Find checkbox associated with 'I understand'
        const labels = Array.from(document.querySelectorAll('label'));
        const confirmLabel = labels.find(l => l.textContent.toLowerCase().includes('understand') || l.textContent.toLowerCase().includes('confirm'));
        
        if (confirmLabel) {
            const checkbox = confirmLabel.querySelector('input[type="checkbox"]');
            if (checkbox && !checkbox.checked) {
                checkbox.click();
                console.log('Gemini: Checked the box');
            }
        }

        // Find the button to proceed
        const buttons = Array.from(document.querySelectorAll('button'));
        const confirmBtn = buttons.find(b => 
            b.textContent.toLowerCase().includes('confirm') || 
            b.textContent.toLowerCase().includes('understand')
        );

        if (confirmBtn) {
            confirmBtn.click();
            console.log('Gemini: Clicked confirm button');
            return true;
        }
        return false;
    })();
    """
    
    try:
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        ws.send(json.dumps({
            'id': 1, 
            'method': 'Runtime.evaluate', 
            'params': {'expression': script, 'returnByValue': True}
        }))
        result = json.loads(ws.recv())
        ws.close()
        
        was_clicked = result.get('result', {}).get('result', {}).get('value')
        if was_clicked:
            print("SUCCESS:Popup dismissed!")
        else:
            print("WARNING:Popup not found or already dismissed.")
            
    except Exception as e:
        print(f"ERROR:Failed to interact with browser: {e}")

if __name__ == "__main__":
    click_udio_confirm()
