#!/usr/bin/env python3

import sys
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QGroupBox, QCheckBox, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from scanner import Scanner
from utils import Utils
import argparse


class ScanWorker(QThread):
    """Worker thread for running scans"""
    progress_updated = Signal(str)
    scan_completed = Signal(dict, float)
    scan_error = Signal(str)
    
    def __init__(self, target, verbose=False, output_file=None):
        super().__init__()
        self.target = target
        self.verbose = verbose
        self.output_file = output_file
        self.scanner = None
        
    def run(self):
        try:
            # Create a mock options object for the scanner
            class Options:
                def __init__(self, target, verbose, output_file):
                    self.target = target
                    self.verbosity = verbose
                    self.write = output_file
            
            options = Options(self.target, self.verbose, self.output_file)
            self.scanner = Scanner(options)
            
            self.progress_updated.emit(f"Starting scan for {self.target}...")
            self.scanner.begin()
            
            # Monitor scan progress
            while self.scanner.running:
                if self.scanner.running == 'cooldown':
                    self.progress_updated.emit("Domain is in cooldown. Waiting...")
                    time.sleep(5)
                else:
                    self.progress_updated.emit("Checking scan status...")
                    self.scanner.check_results()
                    time.sleep(5)
            
            # Scan completed
            elapsed_time = self.scanner.end - self.scanner.start
            self.scan_completed.emit(self.scanner.scan_result, elapsed_time)
            
        except Exception as e:
            self.scan_error.emit(str(e))


class SecurityObserverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scan_worker = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("HTTP Security Observer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("HTTP Security Observer")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #00b4d8; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Input section
        input_group = QGroupBox("Scan Configuration")
        input_layout = QVBoxLayout(input_group)
        
        # Domain input
        domain_layout = QHBoxLayout()
        domain_label = QLabel("Domain:")
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., example.com)")
        domain_layout.addWidget(domain_label)
        domain_layout.addWidget(self.domain_input)
        input_layout.addLayout(domain_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.verbose_checkbox = QCheckBox("Verbose Output")
        self.save_output_checkbox = QCheckBox("Save to File")
        self.output_file_btn = QPushButton("Choose File")
        self.output_file_btn.setEnabled(False)
        self.output_file_path = None
        
        options_layout.addWidget(self.verbose_checkbox)
        options_layout.addWidget(self.save_output_checkbox)
        options_layout.addWidget(self.output_file_btn)
        options_layout.addStretch()
        
        input_layout.addLayout(options_layout)
        
        # Connect signals
        self.save_output_checkbox.toggled.connect(self.output_file_btn.setEnabled)
        self.output_file_btn.clicked.connect(self.choose_output_file)
        
        main_layout.addWidget(input_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready to scan")
        self.status_label.setStyleSheet("color: #90e0ef;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_group)
        
        # Results section
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)
        
        # Create splitter for results
        splitter = QSplitter(Qt.Vertical)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Test", "Status", "Score", "Description"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setVisible(False)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        
        splitter.addWidget(self.results_table)
        splitter.addWidget(self.log_output)
        splitter.setSizes([400, 150])
        
        results_layout.addWidget(splitter)
        main_layout.addWidget(results_group)
        
        # Summary section
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #caf0f8; font-weight: bold;")
        self.summary_label.setVisible(False)
        main_layout.addWidget(self.summary_label)
        
    def set_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
    def choose_output_file(self):
        """Open file dialog to choose output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Scan Results", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.output_file_path = file_path
            self.output_file_btn.setText(f"File: {file_path.split('/')[-1]}")
            
    def start_scan(self):
        """Start the security scan"""
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Input Error", "Please enter a domain to scan.")
            return
            
        # Validate domain (basic check)
        if not self.is_valid_domain(domain):
            QMessageBox.warning(self, "Input Error", "Please enter a valid domain.")
            return
            
        # Disable controls
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Clear previous results
        self.results_table.setVisible(False)
        self.summary_label.setVisible(False)
        self.log_output.clear()
        
        # Start scan worker
        self.scan_worker = ScanWorker(
            domain,
            verbose=self.verbose_checkbox.isChecked(),
            output_file=self.output_file_path if self.save_output_checkbox.isChecked() else None
        )
        
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.scan_completed.connect(self.scan_completed)
        self.scan_worker.scan_error.connect(self.scan_error)
        
        self.scan_worker.start()
        
    def stop_scan(self):
        """Stop the current scan"""
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.terminate()
            self.scan_worker.wait()
            
        self.reset_ui()
        self.log_output.append("Scan stopped by user.")
        
    def update_progress(self, message):
        """Update progress message"""
        self.status_label.setText(message)
        self.log_output.append(message)
        
    def scan_completed(self, results, elapsed_time):
        """Handle scan completion"""
        self.reset_ui()
        
        # Display results in table
        self.display_results(results)
        
        # Show summary
        total_tests = len(results)
        passed_tests = sum(1 for test in results.values() if test['pass'] is True)
        failed_tests = sum(1 for test in results.values() if test['pass'] is False)
        info_tests = total_tests - passed_tests - failed_tests
        
        summary = f"Scan completed in {elapsed_time:.1f}s | "
        summary += f"Total: {total_tests} | "
        summary += f"Passed: {passed_tests} | "
        summary += f"Failed: {failed_tests} | "
        summary += f"Info: {info_tests}"
        
        self.summary_label.setText(summary)
        self.summary_label.setVisible(True)
        
        self.log_output.append(f"Scan completed successfully in {elapsed_time:.1f} seconds.")
        
    def scan_error(self, error_message):
        """Handle scan errors"""
        self.reset_ui()
        self.log_output.append(f"Error: {error_message}")
        QMessageBox.critical(self, "Scan Error", f"An error occurred during the scan:\n{error_message}")
        
    def reset_ui(self):
        """Reset UI to initial state"""
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to scan")
        
    def display_results(self, results):
        """Display scan results in the table"""
        self.results_table.setRowCount(len(results))
        
        for row, (key, test_data) in enumerate(results.items()):
            # Test name
            name_item = QTableWidgetItem(test_data['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 0, name_item)
            
            # Status
            if test_data['pass'] is True:
                status = "✅ PASS"
                color = "#90EE90"  # Light green
            elif test_data['pass'] is False:
                status = "❌ FAIL"
                color = "#FFB6C1"  # Light red
            else:
                status = "⚠️  INFO"
                color = "#FFE4B5"  # Light orange
                
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_item.setBackground(QColor(color))
            self.results_table.setItem(row, 1, status_item)
            
            # Score
            score = f"{test_data['score_modifier']:+d}" if test_data['score_modifier'] != 0 else "0"
            score_item = QTableWidgetItem(score)
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 2, score_item)
            
            # Description
            description = test_data['score_description']
            if description:
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description.replace('\n', ' ').strip()
                description = description[:80] + "..." if len(description) > 80 else description
                
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 3, desc_item)
            
        self.results_table.setVisible(True)
        
    def is_valid_domain(self, domain):
        """Basic domain validation"""
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HTTP Security Observer")
    
    window = SecurityObserverGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 