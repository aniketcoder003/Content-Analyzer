/* Text.tsx */

type TextProps = {
  content: string | null;   // or string | undefined depending on your state
};

function Text({ content }: TextProps) {
  if (!content) {
    return (
      <div className="mt-8 text-center text-gray-500 dark:text-gray-300">
        No content extracted yet
      </div>
    );
  }

  return (
    <div className="mt-6 mx-auto max-w-3xl bg-white dark:bg-gray-900 rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">
        Extracted Text
      </h2>

      <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
        {content}
      </pre>
    </div>
  );
}

export default Text;
