---
name: wiz-code-scan
description: Codex only. Retrieve Wiz Infrastructure-as-Code scan findings, severity counts, and remediation for a source repository. Use for Wiz IaC or code-scan findings, repository Cloud Configuration Findings, or Wiz remediation plans; exclude deployed cloud posture and vulnerability findings unless requested.
---

# Wiz code scan

> **Codex only.** If you are not running in Codex, stop and use this editor's own `wiz-code-scan` skill instead.

Use the `mcp__wiz` MCP. This workflow reads findings by default. Do not edit repository files, create tickets, or change Wiz state unless the user asks; applying a recommendation is a separate change.

## Connect and discover

1. If `mcp__wiz` is not exposed, use Codex tool discovery for Wiz. If it is still unavailable, report that the Wiz MCP is not enabled.
2. Call `discover` with `domain: "cspm"` before the first `execute` in a session. Read the schema for each tool you call. Call `discover` again with `cspm` after a validation error.
3. Call `execute` with `tool_name` and `parameters`.

The Cloud Configuration Findings page filtered by a code repository is the IaC finding set. Deployed-resource configuration findings are a different query.

## Match the code-scan page

1. Resolve the repository with `list_code_repositories` and `search` set to the repository name. `search` is free text, so use only the node whose `name` is exactly `<owner>/<repo>` or whose `url` is the repository URL. When no node or more than one node matches exactly, list the returned names and ask which repository to scan. Pass the matched `id` as a one-item array in `repository_id` on later calls. Although the schema calls this an external ID, the returned `id` is the value to use.
2. For the repository's open code-scan total, call `list_iac_findings_grouped` with `group_by` set to `["SEVERITY"]` and `repository_id`. Leave `status`, `cloud_platform`, and `iac_platform` unset. Pass `status` when the user asks for a different status set. Each group's count is `analytics.totalFindingCount`.
3. Compare per-severity counts with the page's severity bars or the repository's `analytics.cicdScanFindingAnalytics` critical, high, medium, and low counts. The page's donut center is not the total, so do not compare against it. An analytics `totalCount` can exceed the sum of the severity groups.
4. A `cloud_platform` filter removes findings whose cloud platform is null even though those findings appear on the page. Add that filter only after the unfiltered count matches, and state what it removed.
5. Group the matched set by `RULE` and by `RESOURCE_TYPE`. Use `order_by_field: "RESOURCE_COUNT"` to surface the largest groups; do not imply that this order matches a page sorted by severity. The `totalFindingCount` values across all `RULE` groups add up to the severity total.

`list_iac_findings_grouped` uses `first`, requires `group_by`, and returns 10 groups by default. A grouped call is complete only when its `nodes` count equals `totalCount`, the number of groups, so set `first` to at least that number. `list_iac_findings` uses `limit`, rejects `first`, and has no page cursor. Keep `limit` at the default 20, because larger values can return an `INTERNAL` error. A list call is complete only when its `nodes` count equals `totalCount`. Otherwise split the query by `severity`, `rule_id`, or `file_path`, combining those filters, until every call is complete. If a split call still returns fewer nodes than `totalCount`, report that list as truncated and give its `totalCount`.

Set `status` to `["OPEN"]` explicitly on finding-list calls unless the user asks for another status. IaC severities are `INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.

## Remediation

1. List findings with `has_code_remediation: true`. These have one-click edits. The list returns only the file path, not the patch.
2. Call `get_iac_finding` for each one-click finding. Read `fileRemediation` (`before`, `after`, `startLine`, and `remediationType`), `expectedContent`, `foundContent`, `matchContent`, and `remediationInstructions`.
3. For a written plan, fetch one representative finding per rule. The finding's `remediationInstructions` is generic and can use a different resource type from the finding. Apply only the relevant attribute to the cited resource. The parent `rule.remediationInstructions` is CLI guidance and can be empty.
4. Use `list_cloud_configuration_rules` with the rule `id` list and `first` at least the number of rules when you need the exact check or CLI guidance. The payload includes `opaPolicy`, `iacMatchers[].regoCode` (the matcher `type` is the IaC platform), and security category metadata. Extract only the fields needed; do not paste the raw response.

   Template, for a result saved to a file: replace `<saved-file>` with that path. The last argument is the IaC platform of the matchers to print.

   ```bash
   python3 -I -c 'import sys,json; r=json.load(open(sys.argv[1]))["cloudConfigurationRules"]["nodes"]; [print(n["shortId"], n["name"], n["remediationInstructions"], *[m["regoCode"] for m in n["iacMatchers"] or [] if m["type"]==sys.argv[2]], sep="\n") for n in r]' <saved-file> TERRAFORM
   ```

5. `has_remediation_instructions: true` means written guidance exists, not that a code patch exists. `hasTriggerableRemediationFindingCount` on a group is the one-click count.

## Before recommending a change

Read the cited file at `startLine` on the scanned branch and the repository's relevant design or ownership notes.

- A one-click edit can contradict a recorded choice. Name that choice and leave the code unchanged unless the user decides to replace it.
- Wiz guidance that says a setting is create-time or requires recreation identifies a replacement, not an in-place edit, once the provider docs for the pinned version confirm it. Wiz rule text can be outdated.
- A patch for one attribute can still fail a rule that reads additional attributes. Use `expectedContent` and the rule's `regoCode` to identify the full check.
- Findings come from the scanned branch in `get_iac_finding` (`branch.name`), often `main`. Check that branch before treating the local working tree as the scanned code.
- `list_cloud_configurations_findings` with `iac_findings_is_set: true` returns deployed findings linked to code. An empty result does not mean the IaC scan is empty.

If the user asks you to apply fixes, follow the repository instructions and keep code edits on the working branch. Do not claim a finding is resolved until a later Wiz scan confirms it.

## Report

Report findings of `MEDIUM` severity and above. Leave `LOW` and `INFORMATIONAL` findings out unless the user asks, and give their count in one clause.

Lead with one sentence: how many reported findings can be fixed (Levels 1 and 2) and how many stay. Then give the repository, the counts by severity, and whether they match the page.

Scope the report by repository and commit, not by environment: Wiz scans the code on the branch whether or not it is applied. Wiz returns the scan time (`cicdScan.timestamp` from `list_code_repositories`), not the commit. The scanned commit is the head of the branch at that time: `git log origin/<branch> --first-parent -1 --until=<timestamp>`. When the branch moved after the scan, also name the current head that the cited lines refer to, say which code arrived after the scan, and confirm with `git diff <scanned-commit> <head> -- <cited files>` that no later change touches a setting a finding checks. Mention an environment only for a runtime effect of a fix, such as replacing a cluster that several environments share.

Name the sender and the recipient: the team that owns the repository and the team that requires the scan, such as a security or compliance office.

Place each finding in exactly one level. Report by Wiz rule: one row per Wiz rule per level, named with `rule.name` exactly as Wiz returns it, so the reader can find the rule in Wiz, for example to set an exclusion. When a rule's findings fall in different levels, the same `rule.name` has one row in each of those levels: 3 findings split 2 and 1 give a Level 1 row with 2 and a Level 3 row with 1. Do not merge different rules under a label of your own. The row's count is the number of that rule's findings in that level. Put the count and a note such as one-click in the Findings column, not in the name. Take the names and each rule's total from `list_iac_findings_grouped` with `group_by` `["RULE"]`, `repository_id`, `status` `["OPEN"]`, `severity` `["MEDIUM", "HIGH", "CRITICAL"]` and `first` at least the number of groups: each node carries `rule.name` and `analytics.totalFindingCount`, and a rule's counts across the four levels add up to that total. The File cell lists `path:line` for every finding in the row: `filePath` is on each `list_iac_findings` node, and `startLine` is on `get_iac_finding`.

1. **Level 1: in-place update, low risk.** The pinned provider updates the resource in place, and the contract and design do not contradict the change. A rewrite that only lets Wiz read existing code, such as replacing a `dynamic` block, belongs here. When a change needs a prerequisite outside the repository, such as a subscription feature, name it and count those findings separately.
2. **Level 2: forces a new resource, but recommended.** The fix replaces an applied resource, and the risk it removes justifies the replacement. Name what the replacement disrupts and any in-place path the platform offers outside the pinned provider.
3. **Level 3: not necessary.** The environment or the recorded design does not need the change, such as high availability in nonprod, or the service it configures is unused. Mark each row `Forces new` or `In place`.
4. **Level 4: not possible or not supported.** The contract forbids the change, the platform does not support it, two rules conflict, or the rule checks an attribute the pinned provider renamed or removed.

Use one table per level:

- Levels 1 and 2: `| Wiz rule name | Findings | File | Change |`, with `path:line` in File.
- Level 3: `| Wiz rule name | Findings | Change type | Why it is not needed |`.
- Level 4: `| Wiz rule name | Findings | Reason |`.

End with a summary table of the finding count per level. Below it, give the findings fixed and left if Levels 1 and 2 are done, the same for Level 1 only, and how many Level 3 `In place` findings are harmless and would only lower the Wiz count. Then name the next step. Do not paste every CLI block.

## PDF report

Build a PDF only when the user asks for one. It goes to the team that requires the scan, so it states the findings and their fix levels and carries no apply steps: how and when to apply is the repository owner's decision. `scripts/report_template.py` in this skill holds the layout and the report sections, and `scripts/pil-logo.png` is its title-block logo. `<skill-root>` below is the folder that holds this file.

1. Copy `<skill-root>/scripts/report_template.py` to `scripts/build_wiz_code_scan_report.py` and `<skill-root>/scripts/pil-logo.png` to `scripts/pil-logo.png` in the repository, or edit the generator the repository already has.
2. Replace every `<placeholder>` and fill the four level lists with one row per Wiz rule per level. Every row starts with the exact rule name, the count of that rule's findings in that level, and a note on the count that may be empty. Levels 1 and 2 then take the file and the change, Level 3 the change type, the reason and the harmless in-place flag, and Level 4 the reason. The build titles a numbered subsection with each rule name (2.1, 2.2), computes the summary, and stops when a row has the wrong number of values or the levels do not add up to the critical, high and medium counts in `SEVERITY`.
3. Build into `docs/` with `uv run --script scripts/build_wiz_code_scan_report.py docs/<project>-wiz-code-scan-report.pdf`. The script pins `reportlab==4.5.1` as inline metadata, so `uv` installs it in an isolated environment.
4. Check the PDF with Poppler. Template: replace `<pdf>` with the PDF path and `<scratch-dir>` with a temporary folder.

   ```bash
   pdfinfo <pdf> | grep -E 'Title|Subject|Pages'
   pdftotext <pdf> - | grep -n -i -E '(password|passwd|pwd|secret|token|key)=[^[:space:]<]|AccountKey=|SharedAccessKey=|-----BEGIN|eyJ[A-Za-z0-9_-]{10,}\.|[?&]sig=|[A-Za-z0-9+/]{40,}={0,2}'
   pdftotext <pdf> - | grep -n -E '<[A-Za-z][^>]*>'
   pdftoppm -r 80 -png <pdf> <scratch-dir>/page
   ```

   The title and subject show the version. The secret scan and the placeholder scan print nothing. View every page image: header, footer, title block and tables, with no heading alone at the bottom of a page.
5. To issue a new version, change the text, add an entry at the top of `HISTORY`, and rebuild. Never edit the PDF directly.
