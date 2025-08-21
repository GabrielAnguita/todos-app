class UserSelect {
    constructor(element) {
        this.wrapper = element;
        this.trigger = this.wrapper.querySelector('.user-select-trigger');
        this.options = this.wrapper.querySelector('.user-select-options');
        this.hiddenInput = this.wrapper.querySelector('.user-select-input');
        this.fieldName = this.wrapper.dataset.fieldName || 'assigned_user_id';
        
        this.isOpen = false;
        this.selectedValue = this.hiddenInput.value;
        
        // Store instance on the wrapper element for external access
        this.wrapper.userSelectInstance = this;
        
        this.init();
    }
    
    init() {
        // Toggle dropdown on trigger click
        this.trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggle();
        });
        
        // Handle option selection
        this.options.addEventListener('click', (e) => {
            const option = e.target.closest('.user-select-option');
            if (option) {
                e.preventDefault();
                this.selectOption(option);
            }
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.close();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        // Handle keyboard navigation
        this.options.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.options.classList.remove('hidden');
        this.isOpen = true;
        this.trigger.setAttribute('aria-expanded', 'true');
        
        // Don't auto-focus options, let user navigate with keyboard if needed
    }
    
    close() {
        this.options.classList.add('hidden');
        this.isOpen = false;
        this.trigger.setAttribute('aria-expanded', 'false');
        // Don't auto-focus the trigger when closing
    }
    
    selectOption(option) {
        const value = option.dataset.value || '';
        const username = option.dataset.username || '';
        
        // Update hidden input
        this.hiddenInput.value = value;
        this.selectedValue = value;
        
        // Update visual state
        this.updateTriggerDisplay(value, username);
        this.updateCheckmarks(value);
        
        // Close dropdown
        this.close();
        
        // Trigger change event for form handling
        this.hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Custom event for external listeners
        this.wrapper.dispatchEvent(new CustomEvent('userselect:change', {
            detail: { value, username },
            bubbles: true
        }));
    }
    
    updateTriggerDisplay(value, username) {
        const content = this.trigger.querySelector('.flex.items-center');
        const avatar = content.querySelector('.size-6');
        const nameSpan = content.querySelector('span');
        
        if (value && username) {
            // User selected - find the color from the selected option
            const selectedOption = this.options.querySelector(`[data-value="${value}"]`);
            let colorClass = 'bg-blue-500'; // default
            if (selectedOption) {
                const optionAvatar = selectedOption.querySelector('.size-6');
                if (optionAvatar) {
                    // Extract the color class from the option's avatar
                    const classes = optionAvatar.className.split(' ');
                    const bgClass = classes.find(cls => cls.startsWith('bg-'));
                    if (bgClass) {
                        colorClass = bgClass;
                    }
                }
            }
            
            avatar.className = `size-6 shrink-0 rounded-full ${colorClass} flex items-center justify-center text-white text-xs font-medium`;
            avatar.textContent = username.charAt(0).toUpperCase();
            nameSpan.className = 'block truncate font-medium';
            nameSpan.textContent = username;
        } else {
            // No user selected
            avatar.className = 'size-6 shrink-0 rounded-full bg-gray-400 flex items-center justify-center text-gray-800 text-xs';
            avatar.textContent = '?';
            nameSpan.className = 'block truncate text-gray-500 italic';
            nameSpan.textContent = 'Select user...';
        }
    }
    
    updateCheckmarks(selectedValue) {
        // Hide all checkmarks (target the checkmark spans specifically)
        this.options.querySelectorAll('.user-select-option > span.absolute').forEach(checkmark => {
            checkmark.classList.add('hidden');
        });
        
        // Show checkmark for selected option
        const selectedOption = this.options.querySelector(`[data-value="${selectedValue}"]`);
        if (selectedOption) {
            const checkmark = selectedOption.querySelector('span.absolute');
            if (checkmark) {
                checkmark.classList.remove('hidden');
            }
        }
    }
    
    handleKeydown(e) {
        const options = Array.from(this.options.querySelectorAll('.user-select-option'));
        const currentIndex = options.findIndex(option => option === document.activeElement);
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = (currentIndex + 1) % options.length;
                options[nextIndex].focus();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex === 0 ? options.length - 1 : currentIndex - 1;
                options[prevIndex].focus();
                break;
                
            case 'Enter':
            case ' ':
                e.preventDefault();
                if (document.activeElement.classList.contains('user-select-option')) {
                    this.selectOption(document.activeElement);
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                this.close();
                break;
        }
    }
    
    // Public method to set value programmatically
    setValue(value, username) {
        this.hiddenInput.value = value;
        this.selectedValue = value;
        this.updateTriggerDisplay(value, username);
        this.updateCheckmarks(value);
    }
    
    // Public method to get current value
    getValue() {
        return this.selectedValue;
    }
}

// Auto-initialize all user selects on page load
document.addEventListener('DOMContentLoaded', function() {
    const userSelects = document.querySelectorAll('.user-select-wrapper');
    userSelects.forEach(element => {
        new UserSelect(element);
    });
});

// Make UserSelect available globally
window.UserSelect = UserSelect;