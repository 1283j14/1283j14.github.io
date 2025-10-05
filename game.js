document.addEventListener('DOMContentLoaded', () => {
    const textDisplay = document.getElementById('text-display');
    const startButton = document.getElementById('start-button');
    const bookSelect = document.getElementById('book-select');
    const resultDiv = document.getElementById('result');

    let text = '';
    let currentIndex = 0;
    let startTime;
    let mistakeCount = 0;

    // ゲームを初期化して開始
    const startGame = async () => {
        // 結果表示を隠す
        resultDiv.classList.add('hidden');
        
        // APIからテキストを取得
        const selectedBook = bookSelect.value;
        const response = await fetch(`/api/text?book=${selectedBook}`);
        const data = await response.json();
        text = data.text;

        // 変数をリセット
        currentIndex = 0;
        mistakeCount = 0;
        startTime = null;

        // テキストを表示
        updateDisplay();
        
        // キー入力のイベントリスナーを設定
        document.addEventListener('keydown', handleKeyPress);
    };

    // 画面のテキスト表示を更新
    const updateDisplay = () => {
        textDisplay.innerHTML = text.split('').map((char, index) => {
            let className = '';
            if (index < currentIndex) {
                className = 'correct';
            } else if (index === currentIndex) {
                className = 'current';
            }
            return `<span class="${className}">${char}</span>`;
        }).join('');
    };

    // キー入力時の処理
    const handleKeyPress = (e) => {
        // Ctrl, Shift, Altキーなどは無視
        if (e.ctrlKey || e.altKey || e.metaKey) return;
        
        // ゲームオーバーなら何もしない
        if (currentIndex >= text.length) return;

        // ゲーム開始時刻を記録
        if (!startTime) {
            startTime = new Date();
        }

        const typedChar = e.key;
        const expectedChar = text[currentIndex];

        if (typedChar === expectedChar) {
            currentIndex++;
            updateDisplay();
        } else {
            mistakeCount++;
        }
        
        // 全て打ち終わったらゲーム終了
        if (currentIndex === text.length) {
            endGame();
        }
    };
    
    // ゲーム終了時の処理
    const endGame = () => {
        document.removeEventListener('keydown', handleKeyPress);
        const endTime = new Date();
        const elapsedTime = (endTime - startTime) / 1000; // 秒単位
        
        const wpm = Math.round((text.length / 5) / (elapsedTime / 60)); // WPMの計算

        // 結果を表示
        document.getElementById('time').textContent = elapsedTime.toFixed(2);
        document.getElementById('mistakes').textContent = mistakeCount;
        document.getElementById('wpm').textContent = wpm;
        resultDiv.classList.remove('hidden');
    };

    // 開始ボタンにイベントリスナーを設定
    startButton.addEventListener('click', startGame);
});