import { expect, test } from '@playwright/test'

async function hasHorizontalOverflow(page: import('@playwright/test').Page) {
  return page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2)
}

test('Ariva home renders without horizontal overflow', async ({ page }) => {
  await page.goto('/?locale=en')

  await expect(page.getByRole('heading', { name: /Know how Sri Lanka lives/i })).toBeVisible({ timeout: 15000 })
  await expect(page.getByText('Ariva').first()).toBeVisible()
  await expect(page.getByText(/Daily essentials strip/i)).toBeVisible({ timeout: 15000 })
  await expect(page.getByRole('button', { name: 'Cost Desk', exact: true })).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('sources and trilingual UI render without horizontal overflow', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel(/Language/i).selectOption('si')
  await expect(page.getByRole('heading', { name: /ශ්‍රී ලංකාව ජීවත්වන/i })).toBeVisible()
  await page.getByLabel('Primary').getByRole('button', { name: /මූලාශ්‍ර/i }).click()

  await expect(page.getByRole('heading', { name: 'මූලාශ්‍ර', exact: true })).toBeVisible()
  await expect(page.getByText(/ඉහළ මූලාශ්‍ර සෞඛ්‍යය/i)).toBeVisible()
  await expect(page.getByText(/සක්‍රීය මූලාශ්‍ර ලේඛනය/i)).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('authenticated My Ariva Pulse supports save and alert actions', async ({ page }) => {
  test.skip(!process.env.LIFE_E2E_AUTH_TOKEN, 'Set LIFE_E2E_AUTH_TOKEN and VITE_LIFE_TEST_AUTH_TOKEN for authenticated smoke.')

  await page.goto('/?locale=en')
  await expect(page.getByRole('heading', { name: 'My Ariva Pulse' })).toBeVisible({ timeout: 15000 })
  await page.getByRole('button', { name: /Save filters/i }).click()

  await page.getByRole('button', { name: /Signals/i }).click()
  await expect(page.getByRole('heading', { name: 'Signals', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Save' }).first().click()
  await page.getByRole('button', { name: 'Alert' }).first().click()

  await page.getByRole('button', { name: /Today/i }).click()
  await expect(page.getByText(/Saved watches/i)).toBeVisible()
  await expect(page.getByText(/Active rules/i)).toBeVisible()
  expect(await hasHorizontalOverflow(page)).toBe(false)
})
