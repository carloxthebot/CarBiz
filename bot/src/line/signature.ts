// 用 Web Crypto 驗證 LINE 的 X-Line-Signature（HMAC-SHA256 + base64）
const encoder = new TextEncoder()

export async function verifyLineSignature(
  channelSecret: string,
  rawBody: string,
  signature: string | undefined,
): Promise<boolean> {
  if (!signature) return false

  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(channelSecret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  )
  const mac = await crypto.subtle.sign('HMAC', key, encoder.encode(rawBody))
  const expected = btoa(String.fromCharCode(...new Uint8Array(mac)))

  return timingSafeEqual(expected, signature)
}

// 等長字串的常數時間比較，避免 timing attack
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false
  let diff = 0
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return diff === 0
}
