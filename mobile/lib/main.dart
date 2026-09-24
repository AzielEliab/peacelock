import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';

import 'theme.dart';

const genesisPrev = '0000000000000000000000000000000000000000000000000000000000000000';
const absent = 'ABSENT';
const spec = 'PL-WP-0.1';

void main() {
  runApp(const PeaceLockApp());
}

class PeaceLockApp extends StatelessWidget {
  const PeaceLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PeaceLock',
      debugShowCheckedModeBanner: false,
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: ThemeMode.system,
      home: const LedgerPage(),
    );
  }
}

String digest(Map<String, dynamic> fields) {
  final keys = fields.keys.toList()..sort();
  final raw = '{${keys.map((k) => '${jsonEncode(k)}:${jsonEncode(fields[k])}').join(',')}}';
  return sha256.convert(utf8.encode(raw)).toString();
}

class Receipt {
  Receipt(this.fields, this.hash);
  final Map<String, dynamic> fields;
  final String hash;
}

class LedgerPage extends StatefulWidget {
  const LedgerPage({super.key});

  @override
  State<LedgerPage> createState() => _LedgerPageState();
}

class _LedgerPageState extends State<LedgerPage> {
  final _channel = TextEditingController(text: 'email');
  final _note = TextEditingController();
  String _mode = 'SILENCE';
  String _act = 'reply';
  String _duty = 'NONE';
  final _ledger = <Receipt>[];
  String _verify = 'no ledger yet';

  @override
  void dispose() {
    _channel.dispose();
    _note.dispose();
    super.dispose();
  }

  String _now() => DateTime.now().toUtc().toIso8601String().split('.').first + 'Z';

  Map<String, dynamic> _base({required String state, required String prev, required String plId, required String opened}) {
    return {
      'act_class': _act,
      'actor': 'operator',
      'break_reason': null,
      'broken_at': null,
      'channel': _channel.text,
      'counterfactual_act': absent,
      'date_stamp': null,
      'duty_check': _duty,
      'event_kind': 'QUIET',
      'evidence_kind': null,
      'file_name': null,
      'file_sha256': null,
      'inferred_motive': absent,
      'mode': _mode,
      'note': _note.text,
      'opened_at': opened,
      'pl_id': plId,
      'prev_hash': prev,
      'sealed_at': null,
      'spec': spec,
      'state': state,
      'timestamp': null,
      'transcript': absent,
      'window_end': null,
      'window_start': opened,
    };
  }

  void _open() {
    if (_duty == 'HARD_DUTY') {
      setState(() => _verify = 'I6 HARD_DUTY refuses open; write nothing');
      return;
    }
    if (_note.text.length > 140) {
      setState(() => _verify = 'I3 note must be ≤140');
      return;
    }
    final opened = _now();
    final pl = 'pl_${sha256.convert(utf8.encode(opened + _channel.text)).toString().substring(0, 16)}';
    final prev = _ledger.isEmpty ? genesisPrev : _ledger.last.hash;
    final fields = _base(state: 'OPEN', prev: prev, plId: pl, opened: opened);
    setState(() {
      _ledger.add(Receipt(fields, digest(fields)));
      _verify = _runVerify();
    });
  }

  String _runVerify() {
    if (_ledger.isEmpty) return 'no ledger yet';
    for (var i = 0; i < _ledger.length; i++) {
      final r = _ledger[i];
      if (digest(r.fields) != r.hash) return 'BROKEN at $i: hash mismatch';
      final expectPrev = i == 0 ? genesisPrev : _ledger[i - 1].hash;
      if (r.fields['prev_hash'] != expectPrev) return 'BROKEN at $i: prev_hash link';
      if (r.fields['transcript'] != absent) return 'I1 leakage';
    }
    return 'OK  ${_ledger.length} receipt(s). Transcript ABSENT.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('PeaceLock')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Record a silence or an inaction you chose, as a receipt on this device.',
          ),
          const SizedBox(height: 16),
          TextField(controller: _channel, decoration: const InputDecoration(labelText: 'Where')),
          const SizedBox(height: 12),
          FilledButton(onPressed: _open, child: const Text('Open quiet window')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: () => setState(() => _verify = _runVerify()), child: const Text('Check ledger')),
          const SizedBox(height: 8),
          ExpansionTile(
            title: const Text('Advanced'),
            children: [
              const Align(alignment: Alignment.centerLeft, child: Text('What you are keeping')),
              DropdownButton<String>(
                isExpanded: true,
                value: _mode,
                items: const [
                  DropdownMenuItem(value: 'SILENCE', child: Text('Silence')),
                  DropdownMenuItem(value: 'INACTION', child: Text('Inaction')),
                  DropdownMenuItem(value: 'BOTH', child: Text('Silence and inaction')),
                ],
                onChanged: (value) => setState(() => _mode = value ?? 'SILENCE'),
              ),
              const Align(alignment: Alignment.centerLeft, child: Text('Kind of act')),
              DropdownButton<String>(
                isExpanded: true,
                value: _act,
                items: const [
                  DropdownMenuItem(value: 'reply', child: Text('Reply')),
                  DropdownMenuItem(value: 'file', child: Text('File')),
                  DropdownMenuItem(value: 'post', child: Text('Post')),
                  DropdownMenuItem(value: 'other', child: Text('Other')),
                ],
                onChanged: (value) => setState(() => _act = value ?? 'reply'),
              ),
              const Align(alignment: Alignment.centerLeft, child: Text('Duty check')),
              DropdownButton<String>(
                isExpanded: true,
                value: _duty,
                items: const [
                  DropdownMenuItem(value: 'NONE', child: Text('None')),
                  DropdownMenuItem(value: 'ADVISORY', child: Text('Advisory')),
                  DropdownMenuItem(value: 'HARD_DUTY', child: Text('HARD_DUTY')),
                ],
                onChanged: (value) => setState(() => _duty = value ?? 'NONE'),
              ),
              const SizedBox(height: 8),
              TextField(controller: _note, decoration: const InputDecoration(labelText: 'Note, 140 characters or fewer')),
            ],
          ),
          ExpansionTile(
            title: const Text('About'),
            children: const [
              Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: Text(
                  'Author: Aziel Eliab. A receipt stores no transcript. Those fields stay ABSENT. '
                  'HARD_DUTY refuses and writes nothing. This is a receipt for a quiet window you chose. '
                  'It is not a gag-order kit, a wiretap, or third-party binding.',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(_verify, style: const TextStyle(color: kGold)),
          const SizedBox(height: 16),
          for (var i = 0; i < _ledger.length; i++)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  [
                    '#$i  ${_ledger[i].fields['state']}  ${_ledger[i].fields['pl_id']}',
                    'transcript: ${_ledger[i].fields['transcript']}',
                    'hash: ${_ledger[i].hash}',
                  ].join('\n'),
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
