import React, { useRef, useState } from "react";
import axios from "axios";

function Header({ setParsedText }: { setParsedText?: (text: string) => void }) {
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [uploadedFile, setUploadedFile] = useState(false);
    const [isDragging, setIsDragging] = useState(false);

    // sending file to backend
    const processFile = async (file: File) => {
        setUploadedFile(true);

        const formData = new FormData();
        formData.append("file", file);
        // taking the backend url from env file
        const backendUrl = import.meta.env.VITE_BACKEND_URL;
        const parsed = await axios.post(backendUrl, formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        // setting the finally parsed text from backend in order to show it in the frontend
        if (setParsedText) {
            setParsedText(parsed.data.extracted_text);
        }
    };

    // Handle uploading file
    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            await processFile(file);
        }
    };

    // handle dragging file
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files?.[0];
        if (file) {
            await processFile(file);
        }
    };

    return (
        <header className="w-full bg-white dark:bg-gray-900">
            <div className="max-w-4xl mx-auto px-6 py-12 text-center">
                <div className="inline-flex items-center gap-3 mb-4">
                    <svg className="w-10 h-10 text-indigo-500" viewBox="0 0 24 24" fill="none">
                        <path d="M3 12h18M12 3v18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Tool
                    </span>
                </div>

                <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight">
                    <span className="block text-gray-800 dark:text-gray-100">
                        content-
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
                            analyzer
                        </span>
                    </span>
                </h1>

                <p className="mt-4 max-w-2xl mx-auto text-sm sm:text-base text-gray-600 dark:text-gray-300">
                    Parse any pdf or image
                </p>
                <div
                    onClick={handleUploadClick}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`mt-8 border-2 border-dashed rounded-xl p-10 cursor-pointer transition 
                        ${isDragging ? "border-indigo-600 bg-indigo-50 dark:bg-gray-800" : "border-gray-300 dark:border-gray-600"}
                        hover:border-indigo-500`}
                >
                    <p className="text-gray-600 dark:text-gray-300">
                        {uploadedFile ? (
                            <span className="text-indigo-600 font-medium">File uploaded ✔</span>
                        ) : (
                            <>
                                <strong>Click to upload</strong> or drag & drop your file here
                            </>
                        )}
                    </p>
                    <p className="text-xs text-gray-400 mt-2">Supports PDF and Images</p>

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*,.pdf"
                        className="hidden"
                        onChange={handleFileChange}
                    />
                </div>

                <a href="#docs" className="block mt-4 text-sm text-indigo-600 hover:underline dark:text-indigo-400">
                    Learn more
                </a>
            </div>
        </header>
    );
}

export default Header;
