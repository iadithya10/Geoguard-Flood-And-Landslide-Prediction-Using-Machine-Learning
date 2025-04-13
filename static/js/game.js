// Game state management
const gameState = {
    currentDisaster: null,
    score: 0,
    lives: 3,
    level: 1,
    selectedItems: [],
    maxSelection: 4,
    disasters: [],
    completedDisasters: [],
    gameActive: false,
    timeRemaining: 60,
    timerInterval: null
};

// DOM elements to interact with
let gamePlayArea, gameControls, itemSelection, gameScore, gameLevel;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize DOM elements
    gamePlayArea = document.getElementById('game-play-area');
    gameControls = document.getElementById('game-controls');
    itemSelection = document.getElementById('item-selection');
    gameScore = document.getElementById('game-score');
    gameLevel = document.getElementById('game-level');
    
    // Add event listeners to game buttons
    document.getElementById('start-game-btn').addEventListener('click', startGame);
    document.getElementById('disaster-info-btn').addEventListener('click', showDisasterInfo);
    document.getElementById('pause-game-btn').addEventListener('click', togglePauseGame);
    document.getElementById('play-again-btn').addEventListener('click', resetGame);
    
    // Fetch game data
    fetchGameData();
});

// Fetch disaster data from server
function fetchGameData() {
    fetch('/get_game_data')
        .then(response => response.json())
        .then(data => {
            gameState.disasters = data.disasters;
            // Shuffle disasters for random order
            gameState.disasters = shuffleArray([...gameState.disasters]);
        })
        .catch(error => {
            console.error('Error fetching game data:', error);
            alert('Failed to load game data. Please refresh the page.');
        });
}

// Start a new game
function startGame() {
    // Hide start screen, show game
    document.getElementById('game-start-screen').classList.add('d-none');
    gamePlayArea.classList.remove('d-none');
    gameControls.classList.remove('d-none');
    
    // Initialize game state
    gameState.score = 0;
    gameState.level = 1;
    gameState.lives = 3;
    gameState.selectedItems = [];
    gameState.completedDisasters = [];
    gameState.gameActive = true;
    
    // Update UI
    updateScore();
    startNextDisaster();
}

// Start the next disaster challenge
function startNextDisaster() {
    // If we've completed all disasters, end the game with victory
    if (gameState.completedDisasters.length >= gameState.disasters.length) {
        showVictoryScreen();
        return;
    }
    
    // Get next available disaster
    const availableDisasters = gameState.disasters.filter(
        disaster => !gameState.completedDisasters.includes(disaster.id)
    );
    
    if (availableDisasters.length === 0) {
        showVictoryScreen();
        return;
    }
    
    // Select a disaster randomly from available ones
    gameState.currentDisaster = availableDisasters[0];
    
    // Reset selected items
    gameState.selectedItems = [];
    
    // Render disaster scene
    renderDisasterScene();
    
    // Render item selection
    renderItemSelection();
    
    // Start timer
    startTimer();
}

// Render the current disaster scene
function renderDisasterScene() {
    // Set disaster-specific background
    let backgroundImage;
    switch(gameState.currentDisaster.id) {
        case 'flood':
            backgroundImage = 'linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(https://images.unsplash.com/photo-1547683905-f686c993aae5?auto=format&fit=crop&w=800&q=80)';
            break;
        case 'earthquake':
            backgroundImage = 'linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(https://images.unsplash.com/photo-1558389186-438424b00a20?auto=format&fit=crop&w=800&q=80)';
            break;
        case 'hurricane':
            backgroundImage = 'linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(https://images.unsplash.com/photo-1542459900-a2d3e845c231?auto=format&fit=crop&w=800&q=80)';
            break;
        case 'tsunami':
            backgroundImage = 'linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(https://images.unsplash.com/photo-1518398097537-ef986c0fcef5?auto=format&fit=crop&w=800&q=80)';
            break;
        default:
            backgroundImage = 'linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7))';
    }
    
    gamePlayArea.style.backgroundImage = backgroundImage;
    
    // Create disaster information content
    gamePlayArea.innerHTML = `
        <div class="disaster-scene">
            <div class="disaster-info">
                <h2>${gameState.currentDisaster.name} Preparation</h2>
                <p class="lead">${gameState.currentDisaster.description}</p>
                <div class="mt-3">
                    <div class="progress mb-2">
                        <div id="timer-bar" class="progress-bar bg-danger" role="progressbar" style="width: 100%"></div>
                    </div>
                    <p>Select 4 items that would help you prepare for this disaster.</p>
                    <p>Selected: <span id="selected-count">0</span>/4</p>
                </div>
            </div>
        </div>
    `;
}

// Render the item selection interface
function renderItemSelection() {
    // Clear previous items
    itemSelection.innerHTML = '';
    
    // Shuffle items for random order
    const shuffledItems = shuffleArray([...gameState.currentDisaster.items]);
    
    // Create item buttons
    shuffledItems.forEach(item => {
        const itemButton = document.createElement('button');
        itemButton.className = `btn btn-outline-secondary game-item ${gameState.selectedItems.includes(item.id) ? 'selected' : ''}`;
        itemButton.dataset.id = item.id;
        itemButton.innerHTML = `
            <i class="fas fa-box me-2"></i>
            ${item.name}
        `;
        
        // Add click handler
        itemButton.addEventListener('click', () => selectItem(item.id));
        
        // Add to container
        itemSelection.appendChild(itemButton);
    });
}

// Handle item selection
function selectItem(itemId) {
    // If item already selected, deselect it
    if (gameState.selectedItems.includes(itemId)) {
        gameState.selectedItems = gameState.selectedItems.filter(id => id !== itemId);
    } 
    // If we can select more items, add it
    else if (gameState.selectedItems.length < gameState.maxSelection) {
        gameState.selectedItems.push(itemId);
    }
    // If already at max selection, ignore
    else {
        return;
    }
    
    // Update UI
    updateItemSelection();
    
    // If we've selected enough items, enable submit
    if (gameState.selectedItems.length === gameState.maxSelection) {
        showSubmitButton();
    } else {
        hideSubmitButton();
    }
}

// Update the item selection UI
function updateItemSelection() {
    // Update selected count
    const selectedCount = document.getElementById('selected-count');
    if (selectedCount) {
        selectedCount.textContent = gameState.selectedItems.length;
    }
    
    // Update item button styling
    document.querySelectorAll('.game-item').forEach(button => {
        if (gameState.selectedItems.includes(button.dataset.id)) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
}

// Show the submit button when enough items are selected
function showSubmitButton() {
    // Check if submit button already exists
    if (document.getElementById('submit-selection')) {
        return;
    }
    
    const submitButton = document.createElement('button');
    submitButton.id = 'submit-selection';
    submitButton.className = 'btn btn-success mt-3';
    submitButton.innerHTML = '<i class="fas fa-check me-2"></i> Submit Selection';
    submitButton.addEventListener('click', submitSelection);
    
    // Add button after disaster info
    document.querySelector('.disaster-info').appendChild(submitButton);
}

// Hide the submit button
function hideSubmitButton() {
    const submitButton = document.getElementById('submit-selection');
    if (submitButton) {
        submitButton.remove();
    }
}

// Handle submission of selected items
function submitSelection() {
    // Stop the timer
    clearInterval(gameState.timerInterval);
    
    // Calculate score
    let correctCount = 0;
    const currentDisasterItems = gameState.currentDisaster.items;
    
    // Check each selected item
    gameState.selectedItems.forEach(selectedId => {
        const item = currentDisasterItems.find(item => item.id === selectedId);
        if (item && item.correct) {
            correctCount++;
        }
    });
    
    // Award points
    const pointsPerCorrectItem = 25;
    const newPoints = correctCount * pointsPerCorrectItem;
    gameState.score += newPoints;
    
    // Show feedback
    showSelectionFeedback(correctCount, newPoints);
    
    // Mark disaster as completed
    gameState.completedDisasters.push(gameState.currentDisaster.id);
    
    // Update score display
    updateScore();
    
    // Update badge for this disaster type
    updateBadges(gameState.currentDisaster.id);
}

// Show feedback for item selection
function showSelectionFeedback(correctCount, pointsAwarded) {
    // Calculate pass threshold
    const passThreshold = Math.ceil(gameState.maxSelection / 2);
    const passed = correctCount >= passThreshold;
    
    // Create feedback overlay
    const feedbackOverlay = document.createElement('div');
    feedbackOverlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    feedbackOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    feedbackOverlay.style.zIndex = '10';
    
    feedbackOverlay.innerHTML = `
        <div class="text-center text-white p-4 rounded" style="max-width: 80%;">
            <h2>${passed ? 'Good job!' : 'Try again!'}</h2>
            <p class="lead">You selected ${correctCount} correct items out of ${gameState.maxSelection}.</p>
            <p>Points earned: ${pointsAwarded}</p>
            <div class="mt-3 mb-4">
                ${gameState.currentDisaster.items
                    .filter(item => gameState.selectedItems.includes(item.id))
                    .map(item => `
                        <div class="d-flex align-items-center mb-2 ${item.correct ? 'text-success' : 'text-danger'}">
                            <i class="fas ${item.correct ? 'fa-check-circle' : 'fa-times-circle'} me-2"></i>
                            <strong>${item.name}</strong> - ${item.description}
                        </div>
                    `).join('')
                }
            </div>
            <button class="btn btn-primary btn-lg continue-btn">Continue</button>
        </div>
    `;
    
    // Add to game area
    gamePlayArea.appendChild(feedbackOverlay);
    
    // Add continue button handler
    feedbackOverlay.querySelector('.continue-btn').addEventListener('click', () => {
        feedbackOverlay.remove();
        
        // If player failed and has lives left, retry same disaster
        if (!passed && gameState.lives > 1) {
            gameState.lives--;
            gameState.completedDisasters.pop(); // Remove from completed list to retry
            startNextDisaster();
        }
        // If player passed or ran out of lives, go to next disaster
        else {
            // Increment level if player passed
            if (passed) {
                gameState.level++;
                updateScore();
            } 
            // Game over if out of lives
            else if (gameState.lives <= 1) {
                showGameOver();
                return;
            }
            
            // Start next disaster
            startNextDisaster();
        }
    });
}

// Show disaster information modal
function showDisasterInfo() {
    // Get current disaster info
    const disaster = gameState.currentDisaster;
    if (!disaster) return;
    
    // Update modal content
    const modalContent = document.getElementById('disaster-info-content');
    modalContent.innerHTML = `
        <h4>${disaster.name} Information</h4>
        <p>${disaster.description}</p>
        <h5 class="mt-4">Helpful Tips:</h5>
        <ul class="list-group">
            ${getTipsForDisaster(disaster.id).map(tip => 
                `<li class="list-group-item"><i class="fas fa-info-circle me-2 text-info"></i>${tip}</li>`
            ).join('')}
        </ul>
    `;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('disasterInfoModal'));
    modal.show();
}

// Get tips for specific disaster types
function getTipsForDisaster(disasterId) {
    const tips = {
        flood: [
            "Move to higher ground immediately when warnings are issued",
            "Never walk or drive through flood waters",
            "Prepare an emergency kit with water, food, and medication",
            "Secure valuable items above potential water levels",
            "Know your evacuation route in advance"
        ],
        earthquake: [
            "Drop, cover, and hold on during shaking",
            "Stay away from windows and exterior walls",
            "If outdoors, move to an open area away from buildings",
            "Keep a fire extinguisher accessible",
            "Secure heavy furniture to walls"
        ],
        hurricane: [
            "Board up windows and reinforce doors",
            "Store at least 3 days worth of food and water",
            "Keep a battery-powered radio for emergency information",
            "Have evacuation routes planned",
            "Trim trees and branches that could fall"
        ],
        tsunami: [
            "Move inland or to higher ground immediately",
            "A receding ocean is a warning sign - leave immediately",
            "Stay away from the coast until officials give the all-clear",
            "Keep emergency documents in waterproof containers",
            "Know your evacuation routes in advance"
        ]
    };
    
    return tips[disasterId] || ["No specific tips available for this disaster."];
}

// Start the countdown timer
function startTimer() {
    // Reset time
    gameState.timeRemaining = 60;
    
    // Update timer bar
    const timerBar = document.getElementById('timer-bar');
    if (timerBar) {
        timerBar.style.width = '100%';
    }
    
    // Clear any existing interval
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
    }
    
    // Start new interval
    gameState.timerInterval = setInterval(() => {
        gameState.timeRemaining--;
        
        // Update timer bar
        if (timerBar) {
            const percentage = (gameState.timeRemaining / 60) * 100;
            timerBar.style.width = `${percentage}%`;
        }
        
        // Times up!
        if (gameState.timeRemaining <= 0) {
            clearInterval(gameState.timerInterval);
            timeUp();
        }
    }, 1000);
}

// Handle time running out
function timeUp() {
    // Reduce a life
    gameState.lives--;
    
    // Show timeout message
    const timeoutOverlay = document.createElement('div');
    timeoutOverlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    timeoutOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    timeoutOverlay.style.zIndex = '10';
    
    timeoutOverlay.innerHTML = `
        <div class="text-center text-white p-4 rounded" style="max-width: 80%;">
            <h2>Time's Up!</h2>
            <p class="lead">You ran out of time to select items.</p>
            <p>Lives remaining: ${gameState.lives}</p>
            <button class="btn btn-primary btn-lg continue-btn mt-3">Continue</button>
        </div>
    `;
    
    // Add to game area
    gamePlayArea.appendChild(timeoutOverlay);
    
    // Add continue button handler
    timeoutOverlay.querySelector('.continue-btn').addEventListener('click', () => {
        timeoutOverlay.remove();
        
        // If out of lives, game over
        if (gameState.lives <= 0) {
            showGameOver();
        } else {
            // Try the same disaster again
            startNextDisaster();
        }
    });
}

// Toggle pause state
function togglePauseGame() {
    const pauseButton = document.getElementById('pause-game-btn');
    
    if (gameState.gameActive) {
        // Pause the game
        clearInterval(gameState.timerInterval);
        gameState.gameActive = false;
        pauseButton.innerHTML = '<i class="fas fa-play me-2"></i> Resume';
        
        // Show pause overlay
        const pauseOverlay = document.createElement('div');
        pauseOverlay.id = 'pause-overlay';
        pauseOverlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
        pauseOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        pauseOverlay.style.zIndex = '10';
        
        pauseOverlay.innerHTML = `
            <div class="text-center text-white">
                <h2>Game Paused</h2>
                <p>Click Resume to continue playing</p>
            </div>
        `;
        
        gamePlayArea.appendChild(pauseOverlay);
    } else {
        // Resume the game
        startTimer();
        gameState.gameActive = true;
        pauseButton.innerHTML = '<i class="fas fa-pause me-2"></i> Pause';
        
        // Remove pause overlay
        const pauseOverlay = document.getElementById('pause-overlay');
        if (pauseOverlay) {
            pauseOverlay.remove();
        }
    }
}

// Show game over screen
function showGameOver() {
    clearInterval(gameState.timerInterval);
    
    document.getElementById('game-play-area').classList.add('d-none');
    document.getElementById('game-controls').classList.add('d-none');
    document.getElementById('game-over-screen').classList.remove('d-none');
    
    document.getElementById('final-score').textContent = gameState.score;
    document.getElementById('final-level').textContent = gameState.level;
    
    // Update the "You" score in leaderboard
    const yourScore = document.querySelector('#leaderboard-container .leaderboard-item:last-child .badge');
    if (yourScore) {
        yourScore.textContent = gameState.score;
    }
}

// Show victory screen
function showVictoryScreen() {
    clearInterval(gameState.timerInterval);
    
    // Create victory overlay
    const victoryOverlay = document.createElement('div');
    victoryOverlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    victoryOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    victoryOverlay.style.zIndex = '10';
    
    victoryOverlay.innerHTML = `
        <div class="text-center text-white p-5 rounded level-complete">
            <h2>🏆 Congratulations! 🏆</h2>
            <p class="lead">You've completed all disaster challenges!</p>
            <div class="badge-earned my-4">
                <i class="fas fa-award fa-5x"></i>
            </div>
            <p>Final Score: ${gameState.score}</p>
            <p>Levels Completed: ${gameState.level}</p>
            <div class="mt-4">
                <button class="btn btn-primary btn-lg me-3" id="victory-play-again">Play Again</button>
                <a href="/" class="btn btn-secondary btn-lg">Return Home</a>
            </div>
        </div>
    `;
    
    // Add to game area
    gamePlayArea.appendChild(victoryOverlay);
    
    // Add play again button handler
    victoryOverlay.querySelector('#victory-play-again').addEventListener('click', resetGame);
    
    // Update all badges
    updateAllBadges();
    
    // Update the "You" score in leaderboard
    const yourScore = document.querySelector('#leaderboard-container .leaderboard-item:last-child .badge');
    if (yourScore) {
        yourScore.textContent = gameState.score;
    }
}

// Reset the game
function resetGame() {
    // Hide game over screen
    document.getElementById('game-over-screen').classList.add('d-none');
    
    // Remove any overlays
    const overlays = gamePlayArea.querySelectorAll('div[style*="z-index: 10"]');
    overlays.forEach(overlay => overlay.remove());
    
    // Start a new game
    startGame();
}

// Update score display
function updateScore() {
    if (gameScore) gameScore.textContent = gameState.score;
    if (gameLevel) gameLevel.textContent = gameState.level;
}

// Update badges based on completed disasters
function updateBadges(disasterId) {
    const badgeMapping = {
        'flood': 0,
        'earthquake': 2,
        'hurricane': 1,
        'tsunami': 3
    };
    
    const badgeIndex = badgeMapping[disasterId];
    if (badgeIndex !== undefined) {
        const badgeIcon = document.querySelectorAll('#badges-container .badge-item i')[badgeIndex];
        if (badgeIcon) {
            badgeIcon.classList.remove('text-secondary');
            badgeIcon.classList.add('text-warning', 'active');
            
            // Animate badge
            badgeIcon.classList.add('badge-earned');
            setTimeout(() => {
                badgeIcon.classList.remove('badge-earned');
            }, 1500);
        }
    }
}

// Update all badges (for victory)
function updateAllBadges() {
    document.querySelectorAll('#badges-container .badge-item i').forEach(icon => {
        icon.classList.remove('text-secondary');
        icon.classList.add('text-warning', 'active');
    });
    
    // Special animation for master badge
    const masterBadge = document.querySelectorAll('#badges-container .badge-item i')[4];
    if (masterBadge) {
        masterBadge.classList.add('badge-earned');
    }
}

// Utility: Shuffle array
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}
