import { use, useState } from "react";
import Header from "./components/Header";
import Text from "./components/Text";
import axios from "axios";

function App() {
  const [parsedText, setParsedText] = useState<string|null>("This is the parsed text");
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-800">
      <Header setParsedText = {setParsedText}/>
      <Text content={parsedText} />
    </div>
  );
}

export default App;
