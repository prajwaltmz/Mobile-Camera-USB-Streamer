class PCMAudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 1024;
        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (!input || !input[0]) return true;

        const channel = input[0];
        for (let i = 0; i < channel.length; i++) {
            this.buffer[this.bufferIndex++] = channel[i];

            if (this.bufferIndex >= this.bufferSize) {
                // Buffer full, send to main thread
                this.port.postMessage(this.buffer, [this.buffer.buffer]);
                
                // Allocate a new buffer for the next batch
                this.buffer = new Float32Array(this.bufferSize);
                this.bufferIndex = 0;
            }
        }
        return true;
    }
}

registerProcessor('pcm-audio-processor', PCMAudioProcessor);
