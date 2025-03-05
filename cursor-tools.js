// Google Docs Tools for Cursor
// To use: Add this to your Cursor extensions

/**
 * @param {import("@cursorapp/sdk").ExtensionContext} context
 */
module.exports.activate = async function(context) {
  // Register a command to show Google Docs
  const listDocsCommand = context.commands.registerCommand(
    'googleDocs.list',
    async () => {
      const terminal = await context.terminal.createTerminal();
      terminal.show();
      terminal.sendText('python gdoc.py list');
    }
  );

  // Register a command to read a specific Google Doc
  const readDocCommand = context.commands.registerCommand(
    'googleDocs.read',
    async () => {
      const docName = await context.input.showInputBox({
        prompt: 'Enter the name of the Google Doc to read',
        placeHolder: 'Document name'
      });
      
      if (docName) {
        const terminal = await context.terminal.createTerminal();
        terminal.show();
        terminal.sendText(`python gdoc.py read "${docName}"`);
      }
    }
  );

  // Add commands to context.subscriptions to properly dispose them when the extension is deactivated
  context.subscriptions.push(listDocsCommand);
  context.subscriptions.push(readDocCommand);
}; 