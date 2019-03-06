#!/usr/bin/env python3

import configparser
import io
import logging
import netifaces
import os
from enum import Enum

import emoji
import telegram
import zmq

from message_handler import MessageHandler
from zmqchain import ZMQChain, ZMQFailureChain

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger('telegram-bot')


class Commands(Enum):
    START = 1
    VIDEO_STREAM = 2
    SNAPSHOT = 3
    STATS = 4
    REBOOT = 5
    SHUTDOWN = 6

    def __str__(self):
        if self.value == 1:
            return '/start'
        elif self.value == 2:
            return 'video stream'
        elif self.value == 3:
            return 'snapshot'
        elif self.value == 4:
            return 'statistics'
        elif self.value == 5:
            return 'reboot'
        elif self.value == 6:
            return 'shutdown'


mh = MessageHandler(token=config['CREDENTIALS']['TOKEN'],
                    chat_id=config['CREDENTIALS']['CHAT_ID'],
                    commands=[str(c) for c in Commands],
                    queries=['confirm_shutdown',
                             'abort_shutdown',
                             'confirm_reboot',
                             'abort_reboot'])


def emojize(idx):
    return emoji.emojize(':{}:'.format(idx.strip(':')), use_aliases=True)


def fail(bot, update, error_msg):
    emoji = emojize('dizzy_face')
    bot.send_message(chat_id=update.message.chat_id,
                     text='Oh snap! {} {}'.format(error_msg, emoji),
                     parse_mode=telegram.ParseMode.MARKDOWN)


@mh.register_callback(str(Commands.START))
def handle_cmd_start(bot, update):
    logger.info('Processing command /start')

    emoji = emojize('wave')
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hey There{} '
                          'You just have successfully started your personal Babyphone Knecht.'.format(emoji))

    keyboard = [
        ['Video Stream', 'Snapshot'],
        ['Statistics', ],
        ['Reboot', 'Shutdown', ],
    ]
    bot.send_message(chat_id=update.message.chat_id,
                     text='Use the dedicated keyboard to enter your commands.',
                     reply_markup=telegram.ReplyKeyboardMarkup(keyboard))


@mh.register_callback(str(Commands.VIDEO_STREAM))
def handle_cmd_video_stream(bot, update):
    logger.info('Processing command VIDEO_STREAM')

    error_msg = 'Could not figure out URL of video stream'
    interface = config['SYSTEM'].get('NETIFACE', None)
    if interface is None:
        logger.error('Invalid config property: \'NETIFACE\' was not set')
        fail(bot, update, error_msg)
    else:
        try:
            ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        except ValueError:
            logger.error('Invalid config property: interface referenced in \'NETIFACE\' does not exist')
            fail(bot, update, error_msg)
        else:
            port = '8080'
            url = '{}:{}/'.format(ip, port)
            emoji = emojize('computer')
            bot.send_message(chat_id=update.message.chat_id,
                             text='The Video live stream is available at [{}]({}) {}'.format(url, url, emoji),
                             parse_mode=telegram.ParseMode.MARKDOWN)


@mh.register_callback(str(Commands.SNAPSHOT))
def handle_cmd_snapshot_stream(bot, update):
    logger.info('Processing command SNAPSHOT')

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    timeout_in_ms = 1000
    socket.setsockopt(zmq.RCVTIMEO, timeout_in_ms)

    addr = config['CAMERA'].get('SOCKET', None)
    chain = ZMQChain() if addr is not None else ZMQFailureChain('Invalid config property: \'SOCKET\' was not set')
    chain = chain \
        .then(socket.connect, addr) \
        .then(socket.send_string, '') \
        .then(socket.recv)
    binary_img = chain.value

    if binary_img:
        logger.debug('Received bytes from camera')
        bot.send_photo(chat_id=update.message.chat_id, photo=io.BytesIO(binary_img))
    else:
        logger.error(chain.error_msg)
        fail(bot, update, 'Could not receive snapshot')


@mh.register_callback(str(Commands.STATS))
def handle_cmd_stats(bot, update):
    logger.info('Processing command STATS')

    uptime = os.popen('/usr/bin/uptime -p').read().lstrip('up').strip()
    emoji = emojize('alarm_clock')
    bot.send_message(chat_id=update.message.chat_id,
                     text='{} Uptime: {}'.format(emoji, uptime),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def make_inline_keyboard(labels, callback_data):
    return telegram.InlineKeyboardMarkup(
        [[telegram.InlineKeyboardButton(label, callback_data=data) for (label, data) in zip(labels, callback_data)], ])


@mh.register_callback(str(Commands.SHUTDOWN))
def handle_cmd_shutdown(bot, update):
    logger.info('User %d requested shutdown.', update.effective_user.id)

    buttons = make_inline_keyboard(['Confirm', 'Abort'], ['confirm_shutdown', 'abort_shutdown'])
    emoji = emojize('point_up')
    bot.send_message(chat_id=update.message.chat_id,
                     text='Please confirm shutdown {}'.format(emoji),
                     reply_markup=buttons)


@mh.register_callback(str(Commands.REBOOT))
def handle_cmd_reboot(bot, update):
    logger.info('User %d requested reboot.', update.effective_user.id)

    buttons = make_inline_keyboard(['Confirm', 'Abort'], ['confirm_reboot', 'abort_reboot'])
    emoji = emojize('point_up')
    bot.send_message(chat_id=update.message.chat_id,
                     text='Please confirm reboot {}'.format(emoji),
                     reply_markup=buttons)


@mh.register_query_callback('confirm_shutdown')
def handle_query_confirm_shutdown(bot, update):
    logger.info('User %d confirmed shutdown.', update.effective_user.id)

    os.system('/usr/bin/sudo shutdown -h now')


@mh.register_query_callback('abort_shutdown')
def handle_query_abort_shutdown(bot, update):
    logger.info('User %d aborted shutdown.', update.effective_user.id)


@mh.register_query_callback('confirm_reboot')
def handle_query_confirm_reboot(bot, update):
    logger.info('User %d confirmed reboot.', update.effective_user.id)

    os.system('/usr/bin/sudo reboot')


@mh.register_query_callback('abort_reboot')
def handle_query_abort_reboot(bot, update):
    logger.info('User %d aborted reboot.', update.effective_user.id)


def init_logger(log_level):
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    log_level = config['LOGGING']['LOG_LEVEL']
    logger = init_logger(log_level)
    logger.info('Setting log level to {}'.format(log_level))

    mh.run()
