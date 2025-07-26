// Fallback loading system
class LoadingManager {
    constructor() {
        this.progress = 0;
        this.element = document.getElementById('loading');
        this.interval = setInterval(this.update.bind(this), 100);
    }
    
    update() {
        if(this.progress < 90) {
            this.progress += 1;
            this.element.textContent = `Loading... ${this.progress}%`;
        }
    }
    
    complete() {
        clearInterval(this.interval);
        this.element.textContent = "Ready!";
        setTimeout(() => {
            this.element.style.display = 'none';
        }, 500);
    }
}

window.loadingManager = new LoadingManager();
