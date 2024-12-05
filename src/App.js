import React, { useState, useEffect } from 'react';
import './App.css';  // Подключаем стили

const App = () => {
  const [balance, setBalance] = useState(1500);  // Начальный баланс
  const [hasPaid, setHasPaid] = useState(false); // Состояние, проверяющее оплату

  // Обработчик кнопки для начала майнинга
  const handleStartMining = () => {
    alert('Майнинг начался!');
    setBalance(balance + 100); // Добавляем токены
  };

  // Проверка оплаты при загрузке
  useEffect(() => {
    fetch('/api/check-payment')  // Поменяй на свой эндпоинт для проверки
      .then(response => response.json())
      .then(data => setHasPaid(data.hasPaid))  // Устанавливаем состояние после проверки
      .catch(error => console.error('Ошибка при проверке платежа', error));
  }, []);

  return (
    <div className="container">
      <h1 className="header">Майнинг токенов</h1>
      <div className="balance">Баланс: {balance} токенов</div>

      <button
        className={`button ${!hasPaid ? 'disabled' : ''}`}
        onClick={handleStartMining}
        disabled={!hasPaid}
      >
        Начать майнинг
      </button>

      {!hasPaid && (
        <div className="payment-message">
          <p>Чтобы начать майнинг, вам нужно сначала оплатить.</p>
        </div>
      )}

      <div className="footer">© 2024 MiningApp</div>
    </div>
  );
};

export default App;
