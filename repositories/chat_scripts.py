RESERVE_CHAT_PROMPT_SCRIPT = """
local owner = redis.call('HGET', KEYS[1], 'user_id')
if owner ~= ARGV[1] then
    return -1
end

local used = tonumber(redis.call('HGET', KEYS[1], 'prompts_used'))
if used >= tonumber(ARGV[2]) then
    return 0
end

return redis.call('HINCRBY', KEYS[1], 'prompts_used', 1)
"""


SAVE_CHAT_TURN_SCRIPT = """
local owner = redis.call('HGET', KEYS[1], 'user_id')
local remaining = redis.call('PTTL', KEYS[1])

if owner ~= ARGV[1] or remaining <= 0 then
    return -1
end

redis.call('RPUSH', KEYS[2], ARGV[2], ARGV[3])
redis.call('PEXPIRE', KEYS[2], remaining)
return 1
"""