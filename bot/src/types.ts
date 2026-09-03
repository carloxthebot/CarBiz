// LINE webhook payload —— 只列會用到的欄位。

export type LineSource = {
  type: 'user' | 'group' | 'room'
  userId?: string
  groupId?: string
  roomId?: string
}

export type LineMessage = {
  id: string
  type: 'text' | 'image' | 'sticker' | string
  text?: string
}

export type LineEvent = {
  type: string
  webhookEventId?: string
  replyToken?: string
  source?: LineSource
  message?: LineMessage
}

export type LineWebhookBody = {
  events?: LineEvent[]
}
