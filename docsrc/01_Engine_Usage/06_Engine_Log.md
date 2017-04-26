While running, the Driftwood 2D engine will output messages to the console. These can be informational messages about internal engine processes, or warnings and errors. Besides the console, the log can also be directed to a file using the log.file config option. Options may be used to suppress certain kinds of output as well.

Log messages start with a tick count, indicating which tick of the engine the message occurred on, enclosed in square brackets. This is followed by a colon separated chain of smaller messages, starting with the type of message, followed by the domain/subsystem where the message occurred, followed by more information.

An example log message, notated:

<pre>
TICK TYPE  DOMAIN    OPERATION  DATA
[27] INFO: Resource: requested: blue6.json
</pre>

[TOC]

## Kinds of Messages

There are several kinds of messages the engine will output, with different meanings and effects.

### Warnings and Errors
Warnings and Errors are output when something doesn't go as expected. A warning warns about potential issues, while an error warns about definite issues. Both are halting messages; they will cause the engine to shut down if halting is enabled.

Ex.

<pre>
TICK TYPE    DOMAIN FUNCTION    PROBLEM                                          DATA
[0] WARNING: Audio: volume_sfx: cannot adjust sfx volume on nonexistent channel: 9
</pre>

### Fatal Errors
Fatal errors cause the engine to exit immediately without shutting down, and cannot be disabled. They are also not always handled by the logging subsystem, sometimes being output by regular print statement instead; this is because some fatal errors can occur before the logging subsystem is initialized.

Ex.

<pre>
TICK TYPE  DOMAIN  PROBLEM
[0] FATAL: Config: could not read config file
</pre>

### Info Messages
Info messages provide information about internal engine processes, and do not generally indicate a problem. They are only output if the engine is running in verbose mode. There is no consequence to an info message being output.

Ex.

<pre>
TICK TYPE DOMAIN OPERATION DATA
[0] INFO: Cache: uploaded: blue1.json
</pre>

### Script Messages

Script messages are messages output by a print statement inside an event script, and do not necessarily follow the same format. They are also not logged to file. This can be avoided by using the logging subsystem to output messages from your scripts.

## Quiet vs Verbose

This setting is read from the log.verbose option in the config file, or the --quiet or --verbose command line options. In verbose mode, info type messages are output to the log, while in quiet mode they are not. Info messages represent a large volume of output and can either help or get in the way when trying to diagnose a problem, so it is useful to modify the setting sometimes.

## Halting

This setting is read from the log.halting option in the config file, or the --halt or --continue command line options. If halting is enabled, the engine will shut down upon encountering a warning or error message. Otherwise it will attempt to continue unless encountering a fatal error, which always stops the engine right away.

## Message Suppression

It may be desirable to prevent certain messages from appearing in the log. Suppression chains can be defined in the config file as lists of strings inside the log.suppress option, which is itself a list. When a message is to be output, it is checked against the suppression rules. For each item in the suppression chain, if it does not match the item in the same position in the log chain, the message will be output. If all parts of the suppression chain match, the message will be suppressed. A suppression chain can be smaller than the log chain it matches.

Example:

<pre>
(position)       0     1      2         3
Log Chain:   [0] INFO: Cache: uploaded: A_Travellers_Tale.oga

(position)       0       1        2
Suppression:   ["INFO", "Cache", "uploaded"]
This suppression matches.

(position)       0
Suppression:   ["INFO"]
As does this one.

(position)       0       1
Suppression:   ["INFO", "Resource"]
This one does not match, as "Resource" != "Cache" at the same position.
</pre>

There are also halt suppressions, defined in the log.suppress_halt config option. These are structured exactly the same as regular suppressions, but instead of preventing the matching message from being output, they prevent the message from shutting down the engine in halting mode. As an example, the simple suppression rule `["WARNING"]` will helpfully prevent all warnings from halting the engine, and is enabled by default.