from playwright.sync_api import sync_playwright
import time

class Merlin:
    def __init__(self, url = "https://hackmerlin.io/", headless = False):
        self._p = sync_playwright().start()
        self.browser = self._p.chromium.launch(headless=headless,)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        load_time = time.time()
        self.page.goto(url, wait_until="networkidle")
        print(f"Loaded hackmerlin.io in {round((time.time() - load_time) * 100)}ms")

        self.ask_button = self.page.locator("button:has-text('Ask')")
        self.submit_button = self.page.locator("button:has-text('Submit')")
        self.text_input = self.page.locator("textarea")
        self.password_input = self.page.locator("input")
        self.merlin_output = self.page.locator("blockquote")

    def message(self, query):
        self.text_input.fill(query)
        print(f'Sent Query to Merlin: {query}')

        load_time = time.time()
        with self.page.expect_response(lambda r: r.request.resource_type in ("xhr", "fetch") and r.url.startswith("https://hackmerlin.io")):
            self.ask_button.click()
        self.page.evaluate("() => new Promise(requestAnimationFrame)")

        merlin_result = self.merlin_output.inner_text().replace('\n\n– Merlin', '')
        print(f'Merlin Responded "{merlin_result}" in {round((time.time() - load_time) * 100)}ms')

        return merlin_result

    def guess_password(self, password):
        self.password_input.fill(password)
        print(f'Guessing password {password}')

        load_time = time.time()
        with self.page.expect_response(lambda r: r.request.resource_type in ("xhr", "fetch")
                              and r.url.startswith("https://hackmerlin.io")):
            self.submit_button.click()
        self.page.evaluate("() => new Promise(requestAnimationFrame)")

        try:
            self.page.wait_for_function(
                "t => document.body && document.body.innerText.toLowerCase().includes(t)",
                arg="awesome job!",
                timeout=1000
            )
            print(f'The password was correct! ({round((time.time() - load_time) * 100)}ms)')
            self.page.keyboard.press("Enter")
            return True
        except:
            print(f'The password was incorrect! ({round((time.time() - load_time) * 100)}ms)')
        return False
        

    def close(self):
        try:
            self.context.close()
        except Exception:
            pass
        try:
            self.browser.close()
        except Exception:
            pass
        try:
            self._p.stop()
        except Exception:
            pass
