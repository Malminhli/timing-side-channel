-- Pandoc Lua filter used by build_pdf.sh to turn paper.md into a clean
-- academic PDF. It does not change any text of the paper; it only:
--   * takes the author/date paragraph under the title into the title block,
--   * moves the Abstract section (and the Keywords line) into the abstract,
--   * drops the "---" separators used for the Markdown/GitHub view,
--   * includes figures from ../results/ (or a placeholder box if missing),
--   * styles the "Figure N." / "Table N." caption paragraphs,
--   * gives wide tables proportional column widths so they fit the page.

local stringify = pandoc.utils.stringify

local function file_exists(path)
  local f = io.open(path, "r")
  if f then f:close() return true end
  return false
end

local function latex(s) return pandoc.RawBlock("latex", s) end

local function tex_escape(s)
  return (s:gsub("\\", "\\textbackslash{}"):gsub("([#$%%&_{}])", "\\%1"))
end

-- Image-only paragraph -> centred image, or a framed placeholder.
local function figure_block(img)
  local src = img.src
  if file_exists(src) then
    return latex("\\begin{center}\n\\includegraphics[width=0.92\\linewidth,"
      .. "height=0.42\\textheight,keepaspectratio]{" .. src .. "}\n\\end{center}")
  end
  local shown = src:gsub("^%.%./", "")
  io.stderr:write("[paper-filter] missing figure, using placeholder: " .. src .. "\n")
  return latex("\\begin{center}\\fcolorbox{black!35}{black!3}{\\parbox[c][4.2cm][c]"
    .. "{0.85\\linewidth}{\\centering\\sffamily\\small\\color{black!60}"
    .. "Figure not available yet: \\texttt{" .. tex_escape(shown) .. "}\\\\[0.4em]"
    .. "Run the experiments, then re-run \\texttt{paper/build\\_pdf.sh}.}}\\end{center}")
end

-- "**Figure 1.** text" / "**Table 1.** text" -> small caption paragraph.
local function is_caption(para)
  local first = para.content[1]
  if not first or first.t ~= "Strong" then return false end
  local s = stringify(first)
  return s:match("^Figure %d+%.$") or s:match("^Table %d+%.$")
end

-- Column widths: natural width when the table fits, otherwise proportional
-- widths that never make a column narrower than its longest unbreakable
-- token (code such as `hmac_compare_digest` cannot be hyphenated).
local LINE = 92        -- approx. characters per line at \small, 1-inch margins
local CODE = 1.15      -- monospace characters are a bit wider

local function measure_cell(cell)
  local len, longest = 0, 0
  local blocks = pandoc.Blocks(cell.contents)
  blocks:walk({
    Str = function(el)
      local n = utf8.len(el.text) or #el.text
      len = len + n + 1
      if n > longest then longest = n end
    end,
    Code = function(el)
      local n = (utf8.len(el.text) or #el.text) * CODE
      len = len + n + 1
      if n > longest then longest = n end
    end,
  })
  return len, longest
end

local function fix_table(tbl)
  local ncols = #tbl.colspecs
  local body, head, token = {}, {}, {}
  for i = 1, ncols do body[i], head[i], token[i] = 0, 0, 0 end
  local function scan(rows, acc)
    for _, row in ipairs(rows) do
      for i, cell in ipairs(row.cells) do
        if i <= ncols then
          local len, longest = measure_cell(cell)
          if len > acc[i] then acc[i] = len end
          if longest > token[i] then token[i] = longest end
        end
      end
    end
  end
  scan(tbl.head.rows, head)
  for _, b in ipairs(tbl.bodies) do scan(b.body, body) end

  local natural, sum_min, sum_want = 0, 0, 0
  local minw, want = {}, {}
  for i = 1, ncols do
    natural = natural + math.max(body[i], head[i]) + 2
    minw[i] = token[i] + 2
    want[i] = math.max(body[i], math.ceil(head[i] * 0.5), token[i]) + 2
    sum_min = sum_min + minw[i]
    sum_want = sum_want + want[i]
  end
  if natural <= LINE then
    for i = 1, ncols do tbl.colspecs[i] = {tbl.colspecs[i][1], nil} end
    return tbl
  end
  local width = {}
  if sum_want <= LINE then
    for i = 1, ncols do width[i] = want[i] * LINE / sum_want end
  else
    local extra, spread = math.max(0, LINE - sum_min), sum_want - sum_min
    for i = 1, ncols do
      width[i] = minw[i] + (spread > 0 and extra * (want[i] - minw[i]) / spread or 0)
    end
  end
  local total = 0
  for i = 1, ncols do total = total + width[i] end
  for i = 1, ncols do
    tbl.colspecs[i] = {tbl.colspecs[i][1], 0.99 * width[i] / total}
  end
  return tbl
end

local function table_rows(tbl)
  local n = 0
  for _, r in ipairs(tbl.head.rows) do n = n + 1 end
  for _, b in ipairs(tbl.bodies) do n = n + #b.body end
  return n
end

function Pandoc(doc)
  local blocks = doc.blocks
  local meta = doc.meta
  local out = pandoc.List()
  local i = 1

  -- Author / date paragraph right after the title.
  if blocks[1] and blocks[1].t == "Para" and blocks[1].content[1]
      and blocks[1].content[1].t == "Strong" then
    local para = blocks[1].content
    meta.author = pandoc.MetaInlines(para[1].content)
    local rest = pandoc.List()
    for j = 2, #para do
      if not (#rest == 0 and (para[j].t == "SoftBreak" or para[j].t == "LineBreak"
          or para[j].t == "Space")) then
        rest:insert(para[j])
      end
    end
    if #rest > 0 then meta.date = pandoc.MetaInlines(rest) end
    i = 2
  end

  local in_abstract, abstract = false, pandoc.List()
  while i <= #blocks do
    local b = blocks[i]
    if b.t == "HorizontalRule" then
      -- dropped
    elseif b.t == "Header" and stringify(b) == "Abstract" then
      in_abstract = true
    elseif in_abstract and b.t ~= "Header" then
      abstract:insert(b)
    else
      if in_abstract then
        in_abstract = false
        meta.abstract = pandoc.MetaBlocks(abstract)
      end
      if b.t == "Header" and stringify(b) == "References" then
        out:insert(b)
        out:insert(latex("\\begingroup\\small\\setlength{\\parindent}{0pt}"
          .. "\\setlength{\\parskip}{0.35em}\\raggedright"))
        for j = i + 1, #blocks do
          if blocks[j].t == "Para" then
            out:insert(latex("\\hangindent=2.2em\\hangafter=1"))
          end
          out:insert(blocks[j])
        end
        out:insert(latex("\\par\\endgroup"))
        break
      elseif b.t == "Para" and #b.content == 1 and b.content[1].t == "Image" then
        -- keep a figure and its "Figure N." paragraph together on one page
        local nxt = blocks[i + 1]
        if nxt and nxt.t == "Para" and is_caption(nxt) then
          out:insert(latex("\\par\\noindent\\begin{minipage}{\\linewidth}"))
          out:insert(figure_block(b.content[1]))
          out:insert(latex("\\begin{paperCaption}"))
          out:insert(nxt)
          out:insert(latex("\\end{paperCaption}\\end{minipage}\\par\\medskip"))
          i = i + 1
        else
          out:insert(figure_block(b.content[1]))
        end
      elseif b.t == "Para" and is_caption(b) then
        out:insert(latex("\\begin{paperCaption}"))
        out:insert(b)
        out:insert(latex("\\end{paperCaption}"))
      elseif b.t == "Table" then
        -- keep a table on one page: move it if there is not enough room
        -- keep a table on one page (and with a heading right above it)
        local need = latex("\\needspace{" .. (2 * table_rows(b) + 4) .. "\\baselineskip}")
        local prev = out[#out]
        if prev and prev.t == "Header" then
          out:remove(#out)
          out:insert(need)
          out:insert(prev)
        else
          out:insert(need)
        end
        out:insert(latex("\\begingroup\\small"))
        out:insert(fix_table(b))
        out:insert(latex("\\endgroup"))
      else
        out:insert(b)
      end
    end
    i = i + 1
  end
  return pandoc.Pandoc(out, meta)
end
