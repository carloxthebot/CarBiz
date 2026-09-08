// LINE webhook payload —— 只列會用到的欄位。

export type LineSource = {
  type: 'user' | 'group' | 'room'
  userId?: string
  groupId?: string
  roomId?: string
}

export type LineMentionee = {
  index?: number
  length?: number
  type?: 'user' | 'all'
  userId?: string
}

export type LineMessage = {
  id: string
  type: 'text' | 'image' | 'sticker' | string
  text?: string
  mention?: {
    mentionees?: LineMentionee[]
  }
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
