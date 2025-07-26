class SaveSystem {
    static save(key, data) {
        localStorage.setItem(`dontlookdown_${key}`, JSON.stringify(data));
    }
    
    static load(key) {
        const data = localStorage.getItem(`dontlookdown_${key}`);
        return data ? JSON.parse(data) : null;
    }
    
    static delete(key) {
        localStorage.removeItem(`dontlookdown_${key}`);
    }
}

window.SaveSystem = SaveSystem;
