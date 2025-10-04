#!/usr/bin/env python3
"""
Improved login handler for John Pye Auctions with better error handling
"""

import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import logging

class ImprovedLoginHandler:
    """Improved login with robust error handling"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
    
    def login_robust(self) -> bool:
        """Robust login with multiple retry attempts and better error handling"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            self.logger.info(f"🔐 Login attempt {attempt + 1}/{max_attempts}")
            
            try:
                # Navigate to login page
                login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
                self.driver.get(login_url)
                
                # Wait for Cloudflare protection to clear
                if not self._wait_for_cloudflare():
                    self.logger.error("Could not bypass Cloudflare protection")
                    continue
                
                # Take screenshot for debugging
                self.driver.save_screenshot("../data/login_debug.png")
                
                # Wait for page to be fully loaded
                time.sleep(3)
                
                # Handle cookie consent if present
                self._handle_cookie_consent()
                
                # Try to fill login form with retries
                if self._fill_login_form():
                    if self._submit_form():
                        if self._verify_login_success():
                            self.logger.info("✅ Login successful!")
                            return True
                        else:
                            self.logger.warning("Login form submitted but verification failed")
                    else:
                        self.logger.warning("Failed to submit login form")
                else:
                    self.logger.warning("Failed to fill login form")
                
            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} failed: {e}")
                
            # Wait before retry
            if attempt < max_attempts - 1:
                self.logger.info("Waiting before retry...")
                time.sleep(5)
        
        self.logger.error("❌ All login attempts failed")
        return False
    
    def _wait_for_cloudflare(self, timeout=45) -> bool:
        """Wait for Cloudflare protection to clear"""
        self.logger.info("Waiting for Cloudflare protection to clear...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                current_title = self.driver.title
                if "Just a moment" not in current_title and current_title.strip():
                    self.logger.info("Cloudflare protection cleared")
                    return True
            except:
                pass
            time.sleep(2)
        
        self.logger.warning("Cloudflare protection did not clear within timeout")
        return False
    
    def _fill_login_form(self) -> bool:
        """Fill login form with robust element handling"""
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Multiple attempts to find and fill username
            username = os.getenv('JOHNPYE_USERNAME')
            if not username:
                self.logger.error("JOHNPYE_USERNAME not set in environment")
                return False
            
            for attempt in range(3):
                try:
                    # Try different username field selectors
                    username_selectors = ['#username', '[name="username"]', 'input[type="email"]', 'input[placeholder*="email"]']
                    
                    username_field = None
                    for selector in username_selectors:
                        try:
                            username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            self.logger.info(f"Found username field with selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if not username_field:
                        self.logger.error("Could not find username field")
                        return False
                    
                    # Clear and fill username
                    username_field.clear()
                    username_field.send_keys(username)
                    self.logger.info("Username entered successfully")
                    break
                    
                except StaleElementReferenceException:
                    self.logger.warning(f"Stale element on username attempt {attempt + 1}, retrying...")
                    time.sleep(2)
                    continue
            
            # Multiple attempts to find and fill password
            password = os.getenv('JOHNPYE_PASSWORD')
            if not password:
                self.logger.error("JOHNPYE_PASSWORD not set in environment")
                return False
                
            for attempt in range(3):
                try:
                    # Try different password field selectors
                    password_selectors = ['#password', '[name="password"]', 'input[type="password"]']
                    
                    password_field = None
                    for selector in password_selectors:
                        try:
                            password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            self.logger.info(f"Found password field with selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if not password_field:
                        self.logger.error("Could not find password field")
                        return False
                    
                    # Clear and fill password
                    password_field.clear()
                    password_field.send_keys(password)
                    self.logger.info("Password entered successfully")
                    break
                    
                except StaleElementReferenceException:
                    self.logger.warning(f"Stale element on password attempt {attempt + 1}, retrying...")
                    time.sleep(2)
                    continue
            
            # Handle checkboxes (Remember Me and Terms & Conditions)
            self._handle_login_checkboxes()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling login form: {e}")
            return False
    
    def _submit_form(self) -> bool:
        """Submit login form with multiple strategies"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Try different submit strategies
            submit_strategies = [
                # Strategy 1: Find submit button by various selectors
                ('css', 'input[type="submit"]'),
                ('css', 'button[type="submit"]'),
                ('css', '.buttonbox'),
                ('css', '[value="Login"]'),
                ('css', '[value="Sign In"]'),
                # Strategy 2: Form submission
                ('form', None)
            ]
            
            for strategy_type, selector in submit_strategies:
                try:
                    if strategy_type == 'css':
                        submit_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        # Use JavaScript click to avoid interception
                        self.driver.execute_script("arguments[0].click();", submit_element)
                        self.logger.info(f"Form submitted using selector: {selector}")
                        time.sleep(3)
                        return True
                    elif strategy_type == 'form':
                        # Try to submit the form directly
                        form = self.driver.find_element(By.TAG_NAME, 'form')
                        form.submit()
                        self.logger.info("Form submitted directly")
                        time.sleep(3)
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Submit strategy {selector} failed: {e}")
                    continue
            
            self.logger.error("All submit strategies failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error submitting form: {e}")
            return False
    
    def _verify_login_success(self) -> bool:
        """Verify that login was successful"""
        try:
            # Wait for redirect
            time.sleep(5)
            
            current_url = self.driver.current_url
            self.logger.info(f"Current URL after login: {current_url}")
            
            # Check various indicators of successful login
            success_indicators = [
                # URL-based checks
                "Account/LogOn" not in current_url,
                # Content-based checks
                self._check_for_logged_in_content(),
            ]
            
            if any(success_indicators):
                # Take screenshot of successful login
                self.driver.save_screenshot("../data/login_success.png")
                return True
            else:
                # Take screenshot for debugging
                self.driver.save_screenshot("../data/login_failed.png")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying login: {e}")
            return False
    
    def _check_for_logged_in_content(self) -> bool:
        """Check for content that indicates successful login"""
        try:
            # Look for elements that only appear when logged in
            logged_in_indicators = [
                "My Account",
                "Account Details",
                "Bidding",
                "Watchlist",
                "logout",
                "sign out"
            ]
            
            page_text = self.driver.page_source.lower()
            
            for indicator in logged_in_indicators:
                if indicator.lower() in page_text:
                    self.logger.info(f"Found logged-in indicator: {indicator}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking logged-in content: {e}")
            return False
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if present"""
        try:
            # Common cookie consent selectors
            consent_selectors = [
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button[id*="consent"]',
                'button[class*="consent"]',
                '[data-accept="cookies"]',
                '.cookie-accept',
                '#cookie-accept',
                'button:contains("Accept")',
                'button:contains("Accept All")',
                'button:contains("I Accept")',
            ]
            
            for selector in consent_selectors:
                try:
                    # Use a short wait to check if element exists
                    wait = WebDriverWait(self.driver, 2)
                    consent_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    # Click the consent button
                    self.driver.execute_script("arguments[0].click();", consent_button)
                    self.logger.info(f"Clicked cookie consent button with selector: {selector}")
                    time.sleep(2)
                    return
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Cookie consent selector {selector} failed: {e}")
                    continue
            
            # If no specific consent buttons found, look for any button with "accept" text
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['accept', 'agree', 'consent', 'continue']):
                        self.driver.execute_script("arguments[0].click();", button)
                        self.logger.info(f"Clicked consent button with text: {button.text}")
                        time.sleep(2)
                        return
            except Exception as e:
                self.logger.debug(f"Error finding consent buttons by text: {e}")
            
            self.logger.info("No cookie consent popup found or already handled")
            
        except Exception as e:
            self.logger.debug(f"Error handling cookie consent: {e}")
    
    def _handle_login_checkboxes(self):
        """Handle Remember Me and Terms & Conditions checkboxes"""
        try:
            # Find all checkboxes on the page
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            self.logger.info(f"Found {len(checkboxes)} checkboxes on login page")
            
            for i, checkbox in enumerate(checkboxes):
                try:
                    # Get the checkbox label or nearby text to identify it
                    checkbox_context = self._get_checkbox_context(checkbox)
                    self.logger.info(f"Checkbox {i+1}: {checkbox_context}")
                    
                    # Check if this checkbox should be selected
                    should_check = self._should_check_box(checkbox_context)
                    
                    if should_check and not checkbox.is_selected():
                        # Use JavaScript click to avoid interception issues
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        self.logger.info(f"✅ Checked checkbox: {checkbox_context}")
                        time.sleep(0.5)
                    elif checkbox.is_selected():
                        self.logger.info(f"✅ Checkbox already checked: {checkbox_context}")
                    else:
                        self.logger.info(f"⏭️  Skipped checkbox: {checkbox_context}")
                        
                except Exception as e:
                    self.logger.debug(f"Error handling checkbox {i+1}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error handling login checkboxes: {e}")
    
    def _get_checkbox_context(self, checkbox):
        """Get context/label for a checkbox to identify its purpose"""
        try:
            # Try to find associated label
            checkbox_id = checkbox.get_attribute('id')
            if checkbox_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                    return label.text.strip()
                except:
                    pass
            
            # Try to find parent container text
            parent = checkbox.find_element(By.XPATH, '..')
            parent_text = parent.text.strip()
            if parent_text:
                return parent_text[:100]  # Limit length
            
            # Try to find nearby text
            try:
                # Look for text near the checkbox
                nearby_elements = self.driver.find_elements(By.XPATH, 
                    f"//input[@type='checkbox']/following-sibling::*[1] | //input[@type='checkbox']/preceding-sibling::*[1]")
                for elem in nearby_elements:
                    text = elem.text.strip()
                    if text:
                        return text[:100]
            except:
                pass
            
            # Fallback to any attributes
            name = checkbox.get_attribute('name') or 'unnamed'
            value = checkbox.get_attribute('value') or 'no-value'
            return f"name='{name}' value='{value}'"
            
        except Exception as e:
            return f"unknown_checkbox (error: {e})"
    
    def _should_check_box(self, checkbox_context):
        """Determine if a checkbox should be checked based on its context"""
        context_lower = checkbox_context.lower()
        
        # Check for Remember Me checkbox
        if any(phrase in context_lower for phrase in [
            'remember me', 'remember', 'keep me logged in', 'stay logged in'
        ]):
            return True
        
        # Check for Terms & Conditions checkbox  
        if any(phrase in context_lower for phrase in [
            'terms', 'conditions', 'terms & conditions', 'terms and conditions',
            'i accept', 'i agree', 'accept terms', 'agree to terms'
        ]):
            return True
        
        # Check for privacy policy or similar
        if any(phrase in context_lower for phrase in [
            'privacy', 'policy', 'privacy policy'
        ]):
            return True
            
        return False
