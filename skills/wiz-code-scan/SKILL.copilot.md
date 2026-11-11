---
name: wiz-code-scan
description: Pull Wiz IaC code-scan findings and remediation for a repository through the Wiz MCP server (`wiz`). Use whenever the user mentions code scan, code scanning, iac code scan, IaC scan, IaC code scanning, Wiz code scan, Wiz findings, Cloud Configuration Findings, IaC findings, or a Wiz remediation plan. Read-only. Done when the open counts by severity are compared with the Wiz page or the repository analytics, every finding of medium severity or above is placed in one of four fix levels, and every recommended change was checked against the cited file.
---

# Wiz code scan

The Cloud Configuration Findings page, filtered by code repository, is the IaC finding set. Deployed cloud configuration findings are a different query. This skill only reads from Wiz and the repository; it never edits Wiz settings or applies a patch unless the user asks for the edit.

## Before calling

1. The tools are `wiz-discover` and `wiz-execute`. If they are deferred, load them with the tool search tool first. If they are missing or return an authentication error, ask the user to run **MCP: List Servers** in the Command Palette, select `wiz`, and choose Start Server (authenticate when prompted). **Show Output** on the same menu shows the server log.
2. Call `wiz-discover` with `domain` `cspm` before the first `wiz-execute` in the session, and again when a call fails validation. Without `domain`, it returns domain names rather than tool schemas. The `cspm` result may be saved to a file; use the returned path. Print only the compact schemas of the tools you will call.

Template: replace `<saved-file>` with the saved path and list the tool names you need.

```bash
python3 -I -c 'import sys,json; d=json.load(open(sys.argv[1]))[0]; [print(t["name"], t["input_schema"].get("required"), {k:(v.get("type"), (v.get("enum") or v.get("items",{}).get("enum") or [])) for k,v in t["input_schema"]["properties"].items()}) for t in d["tools"] if t["name"] in sys.argv[2:]]' <saved-file> list_code_repositories list_iac_findings_grouped list_iac_findings get_iac_finding
```

`wiz-execute` takes `tool_name` and `parameters`.

## Saved results

A large `wiz-execute` result is saved to a file, and that file can hold the JSON document twice. Parse the first document only; `json.load` fails with `Extra data`.

```bash
python3 -I -B -c 'import sys,json; d=json.JSONDecoder().raw_decode(open(sys.argv[1]).read())[0]; print(list(d))' <saved-file>
```

Read nested fields from `d` and print only the fields you need.

## Match the code-scan page

`list_iac_findings` is the code scan. `list_cloud_configurations_findings` is the deployed-resource scan.

1. Resolve the repository with `list_code_repositories` and `search` set to the repo name. `search` is free text, so use only the node whose `name` is exactly `<owner>/<repo>` or whose `url` is the repository URL. When no node or more than one node matches exactly, list the returned names and ask which repository to scan. Pass the matched `id` as a one-item array in `repository_id` on every later call. The schema calls it an external ID; the returned `id` is the value that works.
2. Count with `list_iac_findings_grouped`, `group_by` `["SEVERITY"]`, and `repository_id` only. Leave `cloud_platform` and `iac_platform` unset on this call. Read `analytics.<severity>SeverityFindingCount` on each node.
3. Compare that count with the page the user is looking at. The severity bars are the finding counts. The donut center is not the total, so do not compare against it. Without the page, compare with `analytics.cicdScanFindingAnalytics` on the repository: its critical, high, medium and low counts match the bars. Compare per severity, because its `totalCount` can exceed the sum of the severity groups.
4. A `cloud_platform` filter drops findings whose cloud platform is null. Those findings still appear on the page. Add `cloud_platform` only after the unfiltered count matches, and say what the filter removed.
5. Group the matched set by `RULE` and by `RESOURCE_TYPE`. `order_by_field` `RESOURCE_COUNT` surfaces the largest groups. The page orders rules by severity, so a medium rule with a small count appears above a low rule with a large count. The grouped call returns 10 groups by default; set `first` above the group count and write a large result to a file for parsing. The sum of `totalFindingCount` over the rule groups equals the severity total.

`list_iac_findings_grouped` uses `first` and requires `group_by`. `list_iac_findings` uses `limit`, rejects `first`, and has no page cursor. Keep `limit` at the default 20, because larger values can return an `INTERNAL` error. A list call is complete only when its `nodes` count equals `totalCount`. Otherwise split the query by `severity`, `rule_id`, or `file_path`, combining those filters, until every call is complete. If a split call still returns fewer nodes than `totalCount`, report that list as truncated and give its `totalCount`.

Default the list to `status` `["OPEN"]` unless the user asks for another status. IaC severities are `INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.

## Remediation

1. List with `has_code_remediation` true. These are the one-click edits. The list returns only the file path.
2. Call `get_iac_finding` with each of those ids. Read `fileRemediation` (`before`, `after`, `startLine`, `remediationType`), `expectedContent`, `foundContent`, `matchContent`, and `remediationInstructions`.
3. For a written plan, call `get_iac_finding` once per rule. The finding's `remediationInstructions` is a generic Terraform example and can name a different resource type from the finding, such as an `azurerm_linux_virtual_machine` snippet on a Windows VM finding. Take the attribute from it and apply it to the cited resource. `rule.remediationInstructions` is the Azure CLI text and is sometimes empty.
4. Use `list_cloud_configuration_rules` with the rule `id` list, and `first` at least the list length (default 15), when you need CLI text for many rules or the exact check. The result may be saved to a file; use the returned path. The payload includes `opaPolicy` (the deployed check), `iacMatchers[].regoCode` (the IaC check for each resource type; the matcher `type` is the IaC platform), and `securitySubCategories`. Extract only what you need; do not paste the raw response into the answer.

```bash
python3 -I -c 'import sys,json; r=json.JSONDecoder().raw_decode(open(sys.argv[1]).read())[0]["cloudConfigurationRules"]["nodes"]; [print(n["shortId"], n["name"], n["remediationInstructions"], *[m["regoCode"] for m in n["iacMatchers"] or [] if m["type"]==sys.argv[2]], sep="\n") for n in r]' <saved-file> TERRAFORM
```

5. `has_remediation_instructions` true means written guidance exists. It does not mean a code patch exists. `hasTriggerableRemediationFindingCount` on a group is the one-click count.

## Advice

Read the cited file at `startLine` and the repository's design notes before recommending a change.

- A one-click edit can contradict a recorded choice. Name that choice and leave the code as recorded.
- Wiz text that says the setting is create-time, or that the resource must be recreated, is a replacement once the provider docs for the pinned version confirm it; Wiz rule text can be outdated. Say so.
- A patch that sets one attribute can leave the rule failing when `expectedContent` also requires a second attribute. The rule's `regoCode` shows which attributes the check reads.
- Findings are from the scanned branch in `branch.name` on `get_iac_finding`, usually `main`. Check that branch before describing the local working tree as the scanned code.
- `list_cloud_configurations_findings` with `iac_findings_is_set` true is a deployed finding linked back to code. An empty result does not mean the code scan is empty.

## Report

Report findings of `MEDIUM` severity and above. Leave `LOW` and `INFORMATIONAL` findings out unless the user asks, and give their count in one clause.

Lead with one sentence: how many reported findings can be fixed (Levels 1 and 2) and how many stay. Then give the repository, the counts by severity, and whether they match the page.

Scope the report by repository and commit, not by environment: Wiz scans the code on the branch whether or not it is applied. Wiz returns the scan time (`cicdScan.timestamp` from `list_code_repositories`), not the commit. The scanned commit is the head of the branch at that time: `git log origin/<branch> --first-parent -1 --until=<timestamp>`. When the branch moved after the scan, also name the current head that the cited lines refer to, say which code arrived after the scan, and confirm with `git diff <scanned-commit> <head> -- <cited files>` that no later change touches a setting a finding checks. Mention an environment only for a runtime effect of a fix, such as replacing a cluster that several environments share.

Name the sender and the recipient: the team that owns the repository and the team that requires the scan, such as a security or compliance office.

Place each finding in exactly one level, and mark one-click findings in their row.

1. **Level 1: in-place update, low risk.** The pinned provider updates the resource in place, and the contract and design do not contradict the change. A rewrite that only lets Wiz read existing code, such as replacing a `dynamic` block, belongs here. When a change needs a prerequisite outside the repository, such as a subscription feature, name it and count those findings separately.
2. **Level 2: forces a new resource, but recommended.** The fix replaces an applied resource, and the risk it removes justifies the replacement. Name what the replacement disrupts and any in-place path the platform offers outside the pinned provider.
3. **Level 3: not necessary.** The environment or the recorded design does not need the change, such as high availability in nonprod, or the service it configures is unused. Mark each row `Forces new` or `In place`.
4. **Level 4: not possible or not supported.** The contract forbids the change, the platform does not support it, two rules conflict, or the rule checks an attribute the pinned provider renamed or removed.

Use one table per level:

- Levels 1 and 2: `| Findings (count) | File | Change |`, with `path:line` in File.
- Level 3: `| Findings | Change type | Why it is not needed |`.
- Level 4: `| Findings | Reason |`.

End with a summary table of the finding count per level. Below it, give the findings fixed and left if Levels 1 and 2 are done, the same for Level 1 only, and how many Level 3 `In place` findings are harmless and would only lower the Wiz count. Then name the next step. Do not paste every CLI block.

## PDF report

Build a PDF only when the user asks for one. It goes to the team that requires the scan, so it states the findings and their fix levels and carries no apply steps: how and when to apply is the repository owner's decision. `scripts/report_template.py` in this skill holds the layout and the report sections, and `scripts/pil-logo.png` is its title-block logo. `<skill-root>` below is the folder that holds this file.

1. Copy `<skill-root>/scripts/report_template.py` to `scripts/build_wiz_code_scan_report.py` and `<skill-root>/scripts/pil-logo.png` to `scripts/pil-logo.png` in the repository, or edit the generator the repository already has.
2. Replace every `<placeholder>` and fill the four level lists. Each row carries its finding count. The build computes the summary, and it stops when the levels do not add up to the critical, high and medium counts in `SEVERITY`.
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
