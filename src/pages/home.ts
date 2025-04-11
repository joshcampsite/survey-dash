import type { Post, Status } from '#/db'
import { html } from '../lib/view'
import { shell } from './shell'

const TODAY = new Date().toDateString()

const STATUS_OPTIONS = [
  '👍',
  '👎',
  '💙',
  '🥹',
  '😧',
  '😤',
  '🙃',
  '😉',
  '😎',
  '🤓',
  '🤨',
  '🥳',
  '😭',
  '😤',
  '🤯',
  '🫡',
  '💀',
  '✊',
  '🤘',
  '👀',
  '🧠',
  '👩‍💻',
  '🧑‍💻',
  '🥷',
  '🧌',
  '🦋',
  '🚀',
]

type Props = {
  statuses: Status[],
  posts: Post[],
  didHandleMap: Record<string, string>
  profile?: { displayName?: string }
  myStatus?: Status
}

export function home(props: Props) {
  return shell({
    title: 'Home',
    content: content(props),
  })
}

function content({ statuses, didHandleMap, profile, myStatus, posts }: Props) {
  return html`<div id="root">
    <div class="error"></div>
    <div id="header">
      <h1>Statusphere x Campsite</h1>
      <p>Set your status and make text posts on the Atmosphere.</p>
    </div>
    <div class="container">
      <div class="card">
        ${profile
          ? html`<form action="/logout" method="post" class="session-form">
              <div>
                Hi, <strong>${profile.displayName || 'friend'}</strong>. What's
                your status today?
              </div>
              <div>
                <button type="submit">Log out</button>
              </div>
            </form>`
          : html`<div class="session-form">
              <div><a href="/login">Log in</a> to set your status!</div>
              <div>
                <a href="/login" class="button">Log in</a>
              </div>
            </div>`}
      </div>
      ${profile || true
        ? html`<form action="/post" method="post" class="text-post-form">
            <div class="form-group">
              <label for="postContent">What's on your mind?</label>
              <textarea
                id="postContent"
                name="postContent"
                rows="3"
                required
                minlength="1"
                maxlength="128"
                placeholder="Enter your post (1-128 characters)"
              ></textarea>
            </div>
            <div class="form-group">
              <button type="submit">Post to Campsite</button>
            </div>
          </form>`
        : ''}
      <form action="/status" method="post" class="status-options">
        ${STATUS_OPTIONS.map(
          (status) =>
            html`<button
              class=${myStatus?.status === status
                ? 'status-option selected'
                : 'status-option'}
              name="status"
              value="${status}"
            >
              ${status}
            </button>`
        )}
      </form>
      ${statuses.map((status, i) => {
        const handle = didHandleMap[status.authorDid] || status.authorDid
        const date = ts(status)
        return html`
          <div class=${i === 0 ? 'status-line no-line' : 'status-line'}>
            <div>
              <div class="status">${status.status}</div>
            </div>
            <div class="desc">
              <a class="author" href=${toBskyLink(handle)}>@${handle}</a>
              ${date === TODAY
                ? `is feeling ${status.status} today`
                : `was feeling ${status.status} on ${date}`}
            </div>
          </div>
        `
      })}
      ${posts.map((post, i) => {
        const handle = didHandleMap[post.authorDid] || post.authorDid
        const date = tp(post)
        return html`
          <div class=${i === 0 ? 'status-line no-line' : 'status-line'}>
            <div>
              <div class="text-wrap">${post.content}</div>
            </div>
            <br>
            <div class="desc">
              <a class="author" href=${toBskyLink(handle)}>@${handle}</a>
            </div>
            <br>
            <div>
              ${date === TODAY
                ? `Today`
                : `${date}`}
            </div>
          </div>
        `
      })}
    </div>
  </div>`
}

function toBskyLink(did: string) {
  return `https://bsky.app/profile/${did}`
}

function ts(status: Status) {
  const createdAt = new Date(status.createdAt)
  const indexedAt = new Date(status.indexedAt)
  if (createdAt < indexedAt) return createdAt.toDateString()
  return indexedAt.toDateString()
}

function tp(post: Post) {
  const createdAt = new Date(post.createdAt)
  const indexedAt = new Date(post.indexedAt)
  if (createdAt < indexedAt) return createdAt.toDateString()
  return indexedAt.toDateString()
}
