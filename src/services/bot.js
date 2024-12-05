// services/bot.js

const axios = require('axios');

// Укажите ваш Telegram Bot Token
const botToken = '7914191127:AAGLnTwVoaAwzNUqLfl32tKn8RWcDU4oyUU';  // Замените на свой токен

// Место хранения состояния пользователей
let paidUsers = {};  // Храним ID пользователей, которые уже заплатили

// Функция для отправки кнопки с предложением начать майнинг
const sendMiningButton = async (chatId) => {
  if (paidUsers[chatId]) {
    await sendMessage(chatId, "Вы уже начали майнинг. Спасибо за поддержку!");
    return;
  }

  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;

  const params = {
    chat_id: chatId,
    text: "Нажмите кнопку для начала майнинга. Чтобы начать, пожалуйста, оплатите.",
    reply_markup: {
      inline_keyboard: [
        [
          {
            text: "Оплатить и начать майнинг",
            callback_data: "start_mining",  // Callback data для обработки
          },
        ],
      ],
    },
  };

  try {
    const response = await axios.post(url, params);
    console.log('Mining button sent:', response.data);
  } catch (error) {
    console.error('Error sending mining button:', error);
  }
};

// Функция для отправки сообщений
const sendMessage = async (chatId, text) => {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;

  const params = {
    chat_id: chatId,
    text,
  };

  try {
    await axios.post(url, params);
  } catch (error) {
    console.error('Error sending message:', error);
  }
};

// Обработка платежей
const handlePayment = (chatId, paymentDetails) => {
  if (paymentDetails.success) {
    paidUsers[chatId] = true;  // Помечаем пользователя как оплатившего
    sendMessage(chatId, "Спасибо за оплату! Майнинг начался.");
  }
};

// Обработка нажатий на кнопки
const handleCallbackQuery = (chatId, callbackData) => {
  if (callbackData === 'start_mining') {
    if (paidUsers[chatId]) {
      sendMessage(chatId, "Вы уже начали майнинг. Спасибо за поддержку!");
    } else {
      sendMiningButton(chatId);  // Отправляем кнопку оплаты
    }
  }
};

module.exports = { sendMiningButton, handleCallbackQuery, handlePayment };
