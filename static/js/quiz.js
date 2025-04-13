
// Quiz state management
let currentQuestionIndex = 0;
let currentLevel = 1;
let userAnswers = {};
let score = 0;
const questionsPerLevel = 10;

document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quiz-container');
    const submitButton = document.getElementById('submit-quiz');
    const resultContainer = document.getElementById('result-container');
    let questions = [];

    // Fetch initial questions for level 1
    fetchQuestionsForLevel(currentLevel);

    function fetchQuestionsForLevel(level) {
        fetch('/get_questions')
            .then(response => response.json())
            .then(data => {
                // Get random 10 questions from the pool
                questions = data.sort(() => Math.random() - 0.5).slice(0, questionsPerLevel);
                displayCurrentQuestion();
            });
    }

    function displayCurrentQuestion() {
        const question = questions[currentQuestionIndex];
        
        quizContainer.innerHTML = `
            <div class="card mb-4">
                <div class="card-header bg-primary text-white d-flex justify-content-between">
                    <h5>Question ${currentQuestionIndex + 1}/${questionsPerLevel} - Level ${currentLevel}</h5>
                    <span>Score: ${score}</span>
                </div>
                <div class="card-body">
                    <p class="question fw-bold">${question.question}</p>
                    ${question.options.map((option, optIndex) => `
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="current-question" 
                                value="${optIndex}" id="opt${optIndex}" 
                                ${userAnswers[currentQuestionIndex] === optIndex ? 'checked' : ''}>
                            <label class="form-check-label" for="opt${optIndex}">${option}</label>
                        </div>
                    `).join('')}
                    <div class="mt-3">
                        <button class="btn btn-info btn-sm" onclick="showHint()">Show Hint</button>
                        ${currentQuestionIndex < questionsPerLevel - 1 ? 
                            '<button class="btn btn-primary float-end" onclick="submitAnswer()">Next</button>' :
                            '<button class="btn btn-success float-end" onclick="submitLevel()">Submit Level</button>'
                        }
                    </div>
                </div>
            </div>
        `;
    }

    window.showHint = function() {
        alert("Hint: Think about the general safety principles and disaster preparedness guidelines!");
    }

    window.submitAnswer = function() {
        const selected = document.querySelector('input[name="current-question"]:checked');
        if (!selected) {
            alert("Please select an answer!");
            return;
        }

        userAnswers[currentQuestionIndex] = parseInt(selected.value);
        
        // Check if answer is correct
        if (parseInt(selected.value) === questions[currentQuestionIndex].answer) {
            score += 10;
        }

        currentQuestionIndex++;
        displayCurrentQuestion();
    }

    window.submitLevel = function() {
        const selected = document.querySelector('input[name="current-question"]:checked');
        if (!selected) {
            alert("Please select an answer!");
            return;
        }

        userAnswers[currentQuestionIndex] = parseInt(selected.value);
        
        // Calculate final score for the level
        const totalScore = Object.keys(userAnswers).reduce((acc, qIndex) => {
            return acc + (userAnswers[qIndex] === questions[qIndex].answer ? 10 : 0);
        }, 0);

        const passScore = 70; // 70% to pass
        const passed = totalScore >= passScore;

        resultContainer.innerHTML = `
            <div class="alert ${passed ? 'alert-success' : 'alert-warning'}">
                <h4>Level ${currentLevel} Results</h4>
                <p>Your score: ${totalScore}/${questionsPerLevel * 10}</p>
                ${passed ? 
                    `<p>Congratulations! You've earned the Level ${currentLevel} Badge!</p>
                     <button class="btn btn-primary" onclick="nextLevel()">Start Level ${currentLevel + 1}</button>` :
                    `<p>Keep practicing! You need ${passScore} points to pass.</p>
                     <button class="btn btn-primary" onclick="retryLevel()">Retry Level</button>`
                }
            </div>
        `;

        if (passed) {
            // Update badge display
            const badgeElement = document.querySelector(`.badge-item:nth-child(${currentLevel})`);
            if (badgeElement) {
                badgeElement.querySelector('i').classList.remove('text-secondary');
                badgeElement.querySelector('i').classList.add('text-warning');
            }
        }

        resultContainer.style.display = 'block';
        quizContainer.style.display = 'none';
    }

    window.nextLevel = function() {
        currentLevel++;
        currentQuestionIndex = 0;
        userAnswers = {};
        resultContainer.style.display = 'none';
        quizContainer.style.display = 'block';
        fetchQuestionsForLevel(currentLevel);
    }

    window.retryLevel = function() {
        currentQuestionIndex = 0;
        userAnswers = {};
        score = 0;
        resultContainer.style.display = 'none';
        quizContainer.style.display = 'block';
        fetchQuestionsForLevel(currentLevel);
    }
});
