
// Game configuration
const gameConfig = {
    currentLevel: 1,
    maxLevels: 20,
    score: 0,
    currentQuestion: 0,
    selectedAnswers: new Set(),
    badges: new Set(),
    questionsPerLevel: 10,
    requiredCorrectAnswers: 6,
    timePerQuestion: 120 // 2 minutes in seconds
};

const levelQuestions = generateLevelQuestions();

function generateLevelQuestions() {
    const allQuestions = {};
    
    // Generate unique questions for all 20 levels
    for (let level = 1; level <= gameConfig.maxLevels; level++) {
        allQuestions[level] = [
            {
                question: `Level ${level} - Which items are essential for disaster preparedness scenario ${level}?`,
                options: ["Emergency Kit", "First Aid Box", "Flashlight", "Water Supply", "Radio", "Maps"],
                correctAnswers: [0, 2, 4]
            },
            {
                question: `Level ${level} - What equipment is needed for safety in situation ${level}?`,
                options: ["Helmet", "Gloves", "Boots", "Whistle", "Rope", "Compass"],
                correctAnswers: [0, 3, 4]
            },
            // Add 8 more unique questions per level
            // This is a sample - in production, you'd have all 10 unique questions per level
        ]
    }
    return allQuestions;
}

let timer;
let timeLeft;

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start-game-btn');
    const gamePlayArea = document.getElementById('game-play-area');
    const badgesContainer = document.getElementById('badges-container');

    if (startButton) {
        startButton.addEventListener('click', startGame);
    }

    function startGame() {
        document.getElementById('game-start-screen').classList.add('d-none');
        gamePlayArea.classList.remove('d-none');
        document.getElementById('game-controls').classList.remove('d-none');
        showQuestion();
        updateUI();
    }

    function startTimer() {
        timeLeft = gameConfig.timePerQuestion;
        clearInterval(timer);
        timer = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();
            if (timeLeft <= 0) {
                clearInterval(timer);
                moveToNextQuestion();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const timerDisplay = document.getElementById('timer-display');
        if (timerDisplay) {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    function showQuestion() {
        const question = levelQuestions[gameConfig.currentLevel][gameConfig.currentQuestion];
        if (!question) return;

        gamePlayArea.innerHTML = `
            <div class="question-container p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h3>Level ${gameConfig.currentLevel} - Question ${gameConfig.currentQuestion + 1}</h3>
                    <div id="timer-display" class="h4">2:00</div>
                </div>
                <p class="mb-4">${question.question}</p>
                <div class="options-container">
                    ${question.options.map((option, index) => `
                        <button class="btn btn-outline-primary m-2 option-btn" data-index="${index}">
                            ${option}
                        </button>
                    `).join('')}
                </div>
                <div class="mt-3">Selected answers: <span id="selected-count">0</span>/3</div>
                <button class="btn btn-success mt-4" id="next-question" disabled>Next Question</button>
                ${gameConfig.currentQuestion === gameConfig.questionsPerLevel - 1 ? 
                    '<button class="btn btn-primary mt-4" id="submit-level">Submit Level</button>' : ''}
            </div>
        `;

        startTimer();
        setupQuestionHandlers();
    }

    function setupQuestionHandlers() {
        const options = document.querySelectorAll('.option-btn');
        const nextButton = document.getElementById('next-question');
        const submitButton = document.getElementById('submit-level');

        options.forEach(option => {
            option.addEventListener('click', () => {
                const index = parseInt(option.dataset.index);
                if (gameConfig.selectedAnswers.has(index)) {
                    gameConfig.selectedAnswers.delete(index);
                    option.classList.remove('active');
                } else if (gameConfig.selectedAnswers.size < 3) {
                    gameConfig.selectedAnswers.add(index);
                    option.classList.add('active');
                }
                
                document.getElementById('selected-count').textContent = gameConfig.selectedAnswers.size;
                nextButton.disabled = gameConfig.selectedAnswers.size !== 3;
            });
        });

        if (nextButton) {
            nextButton.addEventListener('click', moveToNextQuestion);
        }

        if (submitButton) {
            submitButton.addEventListener('click', submitLevel);
        }
    }

    function moveToNextQuestion() {
        clearInterval(timer);
        checkAnswer();
        gameConfig.selectedAnswers.clear();
        gameConfig.currentQuestion++;
        if (gameConfig.currentQuestion < gameConfig.questionsPerLevel) {
            showQuestion();
        }
    }

    function checkAnswer() {
        const question = levelQuestions[gameConfig.currentLevel][gameConfig.currentQuestion];
        const correct = Array.from(gameConfig.selectedAnswers).every(answer => 
            question.correctAnswers.includes(answer)
        );
        if (correct) gameConfig.score++;
    }

    function submitLevel() {
        clearInterval(timer);
        const passScore = gameConfig.requiredCorrectAnswers;
        const passed = gameConfig.score >= passScore;

        if (passed) {
            earnBadge();
            if (gameConfig.currentLevel === gameConfig.maxLevels) {
                showChampionScreen();
            } else {
                gameConfig.currentLevel++;
                gameConfig.currentQuestion = 0;
                gameConfig.score = 0;
                showQuestion();
            }
        } else {
            showFailScreen();
        }
    }

    function earnBadge() {
        const badge = `Level ${gameConfig.currentLevel} Master`;
        gameConfig.badges.add(badge);
        updateBadges();
        showBadgeAnimation(badge);
    }

    function showBadgeAnimation(badge) {
        gamePlayArea.innerHTML = `
            <div class="level-complete-animation">
                <h2>Congratulations!</h2>
                <p>You've earned the ${badge} badge!</p>
                <div class="badge-earned my-4">
                    <i class="fas fa-medal fa-4x text-warning"></i>
                </div>
                <button class="btn btn-primary" onclick="continuePlaying()">Continue to Next Level</button>
            </div>
        `;
    }

    function showChampionScreen() {
        gamePlayArea.innerHTML = `
            <div class="champion-screen text-center">
                <h1>🏆 Congratulations Champion! 🏆</h1>
                <p>You've completed all 20 levels and become a Disaster Preparedness Master!</p>
                <div class="champion-badge my-4">
                    <i class="fas fa-crown fa-5x text-warning"></i>
                </div>
                <button class="btn btn-primary" onclick="location.reload()">Play Again</button>
            </div>
        `;
    }

    function showFailScreen() {
        gamePlayArea.innerHTML = `
            <div class="level-failed-animation">
                <h2>Level Failed</h2>
                <p>You need ${gameConfig.requiredCorrectAnswers} correct answers to pass. Try again!</p>
                <button class="btn btn-primary" onclick="retryLevel()">Retry Level</button>
            </div>
        `;
    }

    window.continuePlaying = () => {
        showQuestion();
    };

    window.retryLevel = () => {
        gameConfig.currentQuestion = 0;
        gameConfig.score = 0;
        showQuestion();
    };
});
