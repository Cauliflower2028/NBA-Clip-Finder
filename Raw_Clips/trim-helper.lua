--ls -1 *.mp4 > playlist.txt
--mpv --playlist=playlist.txt --script=./trim-helper.lua --keep-open=always

local utils = require 'mp.utils'

local start_time = nil
local end_time = nil
local output_file = "cut_list.txt"

function format_time(time_in_seconds)
    if time_in_seconds == nil then return "00:00:00.000" end
    local hours = math.floor(time_in_seconds / 3600)
    local mins = math.floor((time_in_seconds % 3600) / 60)
    local secs = time_in_seconds % 60
    return string.format("%02d:%02d:%06.3f", hours, mins, secs)
end

function set_start_time()
    start_time = mp.get_property("time-pos")
    mp.osd_message(string.format("Start time set: %s", format_time(start_time)))
end

function set_end_time()
    end_time = mp.get_property("time-pos")
    mp.osd_message(string.format("End time set: %s", format_time(end_time)))
end

-- This function is now much smarter
function write_log_entry()
    if start_time == nil or end_time == nil then
        mp.osd_message("Error: Start or End time not set.")
        return
    end

    if start_time >= end_time then
        mp.osd_message("Error: Start time must be before End time.")
        return
    end

    local current_filename = mp.get_property("filename")
    
    -- 1. Read all existing lines from the cut_list.txt file
    local lines = {}
    local file = io.open(output_file, "r")
    if file then
        for line in file:lines() do
            -- 2. Keep only the lines that are NOT for the current video
            if not string.find(line, current_filename, 1, true) then
                table.insert(lines, line)
            end
        end
        file:close()
    end
    
    -- 3. Create the new line for the current video
    local formatted_start = format_time(start_time)
    local formatted_end = format_time(end_time)
    local new_line = string.format("%s,%s,%s", current_filename, formatted_start, formatted_end)
    table.insert(lines, new_line)
    
    -- 4. Overwrite the file with the updated list of lines
    file = io.open(output_file, "w")
    if file then
        file:write(table.concat(lines, "\n"))
        file:close()
        mp.osd_message(string.format("Log updated for: %s", current_filename))
        -- NOTE: mp.command("quit") has been removed as you requested.
    else
        mp.osd_message(string.format("Error writing to %s", output_file))
    end
end

mp.add_key_binding("s", "set-start", set_start_time)
mp.add_key_binding("e", "set-end", set_end_time)
mp.add_key_binding("w", "write-log", write_log_entry)